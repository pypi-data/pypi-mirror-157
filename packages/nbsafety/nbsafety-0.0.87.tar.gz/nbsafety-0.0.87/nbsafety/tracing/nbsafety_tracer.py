# -*- coding: utf-8 -*-
import ast
import logging
import symtable
from collections import defaultdict
from types import FrameType
from typing import cast, Any, Dict, List, Optional, Set, Tuple, Union

import astunparse
import pyccolo as pyc
from IPython import get_ipython

from nbsafety.analysis.live_refs import compute_live_dead_symbol_refs
from nbsafety.data_model.code_cell import cells
from nbsafety.data_model.data_symbol import DataSymbol
from nbsafety.data_model.namespace import Namespace
from nbsafety.data_model.scope import Scope
from nbsafety.data_model.timestamp import Timestamp
from nbsafety.run_mode import SafetyRunMode
from nbsafety.singletons import nbs, SingletonBaseTracer
from nbsafety.tracing.mutation_event import (
    ArgMutate,
    ListInsert,
    ListPop,
    ListRemove,
    MutatingMethodEventNotYetImplemented,
    StandardMutation,
    resolve_mutating_method,
)
from nbsafety.tracing.mutation_special_cases import (
    METHODS_WITHOUT_MUTATION_EVEN_FOR_NULL_RETURN,
    METHODS_WITH_MUTATION_EVEN_FOR_NON_NULL_RETURN,
)
from nbsafety.tracing.safety_ast_rewriter import SafetyAstRewriter
from nbsafety.tracing.symbol_resolver import resolve_rval_symbols
from nbsafety.tracing.trace_stmt import TraceStatement
from nbsafety.tracing.mutation_event import MutationEvent
from nbsafety.tracing.utils import match_container_obj_or_namespace_with_literal_nodes
from nbsafety.types import SupportedIndexType


AttrSubVal = SupportedIndexType
NodeId = int
ObjId = int
MutationCandidate = Tuple[
    Tuple[Any, Optional[str], Optional[str]],
    MutationEvent,
    List[Set[DataSymbol]],
    List[Any],
]
Mutation = Tuple[int, MutationEvent, Set[DataSymbol], List[Any]]
SavedStoreData = Tuple[Namespace, Any, AttrSubVal, bool]
SavedDelData = Tuple[Namespace, Any, AttrSubVal, bool]
SavedComplexSymbolLoadData = Tuple[Namespace, Any, AttrSubVal, bool, Optional[str]]


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


ARG_MUTATION_EXCEPTED_MODULES = {
    "alt",
    "altair",
    "display",
    "logging",
    "matplotlib",
    "pyplot",
    "plot",
    "plt",
    "seaborn",
    "sns",
    "widget",
}


reactive_spec = pyc.AugmentationSpec(
    aug_type=pyc.AugmentationType.prefix, token="$", replacement=""
)
blocking_spec = pyc.AugmentationSpec(
    aug_type=pyc.AugmentationType.prefix, token="$:", replacement=""
)


class ModuleIniter(pyc.BaseTracer):
    @pyc.register_raw_handler(pyc.init_module)
    def init_cell(self, _obj, _node_id, frame: FrameType, *_, **__):
        nbs().set_name_to_cell_num_mapping(frame)
        for tracer in pyc._TRACER_STACK:
            tracer._tracing_enabled_files.add(frame.f_code.co_filename)


class StackFrameManager(SingletonBaseTracer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_depth = 0

    @pyc.register_raw_handler((pyc.call, pyc.return_))
    def handle_first_ipython_frame(
        self,
        _ret: Any,
        _node_id: None,
        frame: FrameType,
        event: pyc.TraceEvent,
        *_,
        **__,
    ):
        if frame.f_code.co_name == "<traced_lambda>":
            return pyc.SkipAll
        # IPython quirk -- every line in outer scope apparently wrapped in lambda
        # We want to skip the outer 'call' and 'return' for these
        if event == pyc.call:
            self.call_depth += 1
            if self.call_depth == 1:
                return pyc.SkipAll
        elif event == pyc.return_:
            self.call_depth -= 1
            if nbs().is_develop:
                assert self.call_depth >= 0
            if self.call_depth == 0:
                return pyc.SkipAll


class SafetyTracer(StackFrameManager):
    ast_rewriter_cls = SafetyAstRewriter

    def should_propagate_handler_exception(
        self, evt: pyc.TraceEvent, exc: Exception
    ) -> bool:
        return SafetyRunMode.get() == SafetyRunMode.DEVELOP

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tracing_enabled_files.discard(self.defined_file)
        with self.persistent_fields():
            self.reactive_node_ids: Set[int] = self.augmented_node_ids_by_spec[
                reactive_spec
            ]
            self.blocking_node_ids: Set[int] = self.augmented_node_ids_by_spec[
                blocking_spec
            ]
        self._module_stmt_counter = 0
        self._saved_stmt_ret_expr: Optional[Any] = None
        self._seen_loop_ids: Set[NodeId] = set()
        self._seen_functions_ids: Set[NodeId] = set()
        self.prev_event: Optional[pyc.TraceEvent] = None
        self.prev_trace_stmt: Optional[TraceStatement] = None
        self.seen_stmts: Set[NodeId] = set()
        self.traced_statements: Dict[NodeId, TraceStatement] = {}
        self.node_id_to_loaded_symbols: Dict[NodeId, List[DataSymbol]] = defaultdict(
            list
        )
        self.node_id_to_saved_store_data: Dict[NodeId, SavedStoreData] = {}
        self.node_id_to_saved_live_subscript_refs: Dict[NodeId, Set[DataSymbol]] = {}
        self.node_id_to_saved_del_data: Dict[NodeId, SavedDelData] = {}
        self.node_id_to_loaded_literal_scope: Dict[NodeId, Namespace] = {}
        self.node_id_to_saved_dict_key: Dict[NodeId, Any] = {}
        self.this_stmt_updated_symbols: Set[DataSymbol] = set()
        try:
            self.cur_cell_symtab: symtable.SymbolTable = symtable.symtable(
                cells().current_cell().sanitized_content(),
                f"<cell-{cells().exec_counter()}>",
                "exec",
            )
        except:
            # it'll just give a syntax error anyway when we try to execute;
            # do this just for the benefit of the type checker
            self.cur_cell_symtab: symtable.SymbolTable = symtable.symtable(
                "", f"<cell-{cells().exec_counter()}>", "exec"
            )

        self.call_stack: pyc.TraceStack = self.make_stack()
        with self.call_stack.register_stack_state():
            # everything here should be copyable
            self.prev_trace_stmt_in_cur_frame: Optional[TraceStatement] = None
            self.prev_node_id_in_cur_frame: Optional[NodeId] = None
            self.mutations: List[Mutation] = []
            self.saved_assign_rhs_obj: Optional[Any] = None
            # this one gets set regardless of whether tracing enabled
            self.next_stmt_node_id: Optional[NodeId] = None

            self.pending_class_namespaces: List[Namespace] = []

            with self.call_stack.needing_manual_initialization():
                self.cur_frame_original_scope: Scope = nbs().global_scope
                self.active_scope: Scope = nbs().global_scope
                self.inside_anonymous_call = False

            self.lexical_call_stack: pyc.TraceStack = self.make_stack()
            with self.lexical_call_stack.register_stack_state():
                self.num_args_seen = 0
                self.first_obj_id_in_chain: Optional[ObjId] = None
                self.top_level_node_id_for_chain: Optional[NodeId] = None
                self.saved_complex_symbol_load_data: Optional[
                    SavedComplexSymbolLoadData
                ] = None
                self.prev_node_id_in_cur_frame_lexical: Optional[NodeId] = None
                self.mutation_candidate: Optional[MutationCandidate] = None

                self.lexical_literal_stack: pyc.TraceStack = self.make_stack()
                with self.lexical_literal_stack.register_stack_state():
                    # `None` means use 'cur_frame_original_scope'
                    self.active_literal_scope: Optional[Namespace] = None

    @property
    def syntax_augmentation_specs(self) -> List[pyc.AugmentationSpec]:
        return [blocking_spec, reactive_spec]

    @property
    def should_patch_meta_path(self) -> bool:
        return False

    def module_stmt_counter(self) -> int:
        return self._module_stmt_counter

    # TODO: use stack mechanism to automate this?
    def after_stmt_reset_hook(self) -> None:
        self.mutations.clear()
        self.mutation_candidate = None
        self.active_scope = self.cur_frame_original_scope
        self.first_obj_id_in_chain = None
        self.top_level_node_id_for_chain = None
        self.saved_complex_symbol_load_data = None
        self.active_literal_scope = None
        self.node_id_to_loaded_literal_scope.clear()
        self.node_id_to_saved_dict_key.clear()
        self.prev_node_id_in_cur_frame = None
        self.saved_assign_rhs_obj = None
        nbs().updated_symbols |= self.this_stmt_updated_symbols
        self.this_stmt_updated_symbols.clear()
        self._seen_functions_ids.clear()
        # don't clear the lexical stacks because line magics can
        # mess with when an 'after_stmt' gets emitted, and anyway
        # these should be pushed / popped appropriately by ast events

    def _handle_call_transition(self, trace_stmt: TraceStatement):
        # ensures we only handle del's and not delitem's
        self.node_id_to_saved_del_data.clear()
        new_scope = trace_stmt.get_post_call_scope()
        with self.call_stack.push():
            # TODO: figure out a better way to determine if we're inside a lambda
            #  could this one lead to a false negative if a lambda is in the default of a function def kwarg?
            self.inside_anonymous_call = not isinstance(
                trace_stmt.stmt_node,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
            )
            self.cur_frame_original_scope = new_scope
            self.active_scope = new_scope
        self.prev_trace_stmt_in_cur_frame = self.prev_trace_stmt = trace_stmt

    def _check_prev_stmt_done_executing_hook(
        self, event: pyc.TraceEvent, trace_stmt: TraceStatement
    ):
        if event == pyc.after_stmt and self.is_tracing_enabled:
            trace_stmt.finished_execution_hook()
        elif event == pyc.return_ and self.prev_event not in (
            pyc.call,
            pyc.exception,
        ):
            # ensuring prev != call ensures we're not inside of a stmt with multiple calls (such as map w/ lambda)
            if self.prev_trace_stmt is not None:
                self.prev_trace_stmt.finished_execution_hook()
            # prev_overall = self.prev_trace_stmt
            # if prev_overall is not None and prev_overall is not self._stack[-1][0]:
            #     # this condition ensures we're not inside of a stmt with multiple calls (such as map w/ lambda)
            #     prev_overall.finished_execution_hook()

    def _handle_return_transition(self, trace_stmt: TraceStatement, ret: Any):
        try:
            inside_anonymous_call = self.inside_anonymous_call
            try:
                return_to_stmt: TraceStatement = self.call_stack.get_field(
                    "prev_trace_stmt_in_cur_frame"
                )
            except IndexError:
                # then the first call was triggered from inside library code;
                # skip the transition and disable tracing in case this call
                # happens in a loop; we won't catch it in our normal tracing
                # disabler since it's the first call
                self._disable_tracing()
                return
            assert return_to_stmt is not None
            if self.prev_event != pyc.exception:
                # exception events are followed by return events until we hit an except clause
                # no need to track dependencies in this case
                if isinstance(return_to_stmt.stmt_node, ast.ClassDef):
                    return_to_stmt.class_scope = cast(
                        Namespace, self.cur_frame_original_scope
                    )
                elif (
                    isinstance(trace_stmt.stmt_node, ast.Return)
                    or inside_anonymous_call
                ):
                    if not trace_stmt.lambda_call_point_deps_done_once:
                        trace_stmt.lambda_call_point_deps_done_once = True
                        maybe_lambda_sym = nbs().statement_to_func_cell.get(
                            id(trace_stmt.stmt_node), None
                        )
                        maybe_lambda_node = None
                        if maybe_lambda_sym is not None:
                            maybe_lambda_node = maybe_lambda_sym.stmt_node
                        if (
                            inside_anonymous_call
                            and maybe_lambda_node is not None
                            and isinstance(maybe_lambda_node, ast.Lambda)
                        ):
                            rvals = resolve_rval_symbols(maybe_lambda_node.body)
                        else:
                            rvals = resolve_rval_symbols(trace_stmt.stmt_node)
                        dsym_to_attach = None
                        if len(rvals) == 1:
                            dsym_to_attach = next(iter(rvals))
                            if dsym_to_attach.obj_id != id(ret):
                                dsym_to_attach = None
                        if dsym_to_attach is None and len(rvals) > 0:
                            dsym_to_attach = self.cur_frame_original_scope.upsert_data_symbol_for_name(
                                "<return_sym_%d>" % id(ret),
                                ret,
                                rvals,
                                trace_stmt.stmt_node,
                                is_anonymous=True,
                            )
                        if dsym_to_attach is not None:
                            return_to_node_id = self.call_stack.get_field(
                                "prev_node_id_in_cur_frame"
                            )
                            # logger.error("prev seen: %s", ast.dump(self.ast_node_by_id[return_to_node_id]))
                            try:
                                call_node_id = self.call_stack.get_field(
                                    "lexical_call_stack"
                                ).get_field("prev_node_id_in_cur_frame_lexical")
                                call_node = cast(
                                    ast.Call, self.ast_node_by_id[call_node_id]
                                )
                                # logger.error("prev seen outer: %s", ast.dump(self.ast_node_by_id[call_node_id]))
                                total_args = len(call_node.args) + len(
                                    call_node.keywords
                                )
                                num_args_seen = self.call_stack.get_field(
                                    "num_args_seen"
                                )
                                logger.warning("num args seen: %d", num_args_seen)
                                if total_args == num_args_seen:
                                    return_to_node_id = call_node_id
                                else:
                                    assert num_args_seen < total_args
                                    if num_args_seen < len(call_node.args):
                                        return_to_node_id = id(
                                            call_node.args[num_args_seen]
                                        )
                                    else:
                                        return_to_node_id = id(
                                            call_node.keywords[
                                                num_args_seen - len(call_node.args)
                                            ].value
                                        )
                            except IndexError:
                                pass
                            # logger.error("use node %s", ast.dump(self.ast_node_by_id[return_to_node_id]))
                            self.node_id_to_loaded_symbols[return_to_node_id].append(
                                dsym_to_attach
                            )
        finally:
            if self.is_tracing_enabled:
                self.call_stack.pop()
            if nbs().is_develop and len(self.call_stack) == 0:
                assert self.call_depth == 1

    def state_transition_hook(
        self,
        event: pyc.TraceEvent,
        trace_stmt: TraceStatement,
        ret: Any,
    ):
        self._check_prev_stmt_done_executing_hook(event, trace_stmt)

        if event == pyc.call:
            self._handle_call_transition(trace_stmt)
        if event == pyc.return_:
            self._handle_return_transition(trace_stmt, ret)
        self.prev_trace_stmt = trace_stmt
        self.prev_event = event

    @staticmethod
    def _partial_resolve_ref(ref: Union[str, int, ast.AST]) -> Union[str, int]:
        if isinstance(ref, ast.Starred):
            ref = ref.value
        if isinstance(ref, ast.Name):
            ref = ref.id
        if isinstance(ref, ast.AST):
            ref = id(ref)
        return ref

    def _resolve_store_data_for_simple_target(self, target: str, frame: FrameType):
        scope = self.cur_frame_original_scope
        lut = frame.f_locals
        if scope.symtab is not None:
            try:
                target_sym = scope.symtab.lookup(target)
                # this nonsense is necessary because the "is_nonlocal" method
                # is not available on Python <= 3.7;
                # the below check seems to work consistently across all Python versions
                is_nonlocal = getattr(
                    target_sym,
                    "is_nonlocal",
                    lambda: not target_sym.is_global()
                    and target_sym.is_assigned()
                    and target_sym.is_free(),
                )()
                if is_nonlocal:
                    scope = scope.parent_scope
                elif target_sym.is_global():
                    lut = frame.f_globals
                    scope = nbs().global_scope
            except KeyError:
                pass
        try:
            obj = lut[target]
        except KeyError:
            obj = frame.f_globals[target]
            scope = nbs().global_scope
        return scope, target, obj, False, set()

    def resolve_store_data_for_target(
        self, target: Union[str, int, ast.AST], frame: FrameType
    ) -> Tuple[Scope, AttrSubVal, Any, bool, Set[DataSymbol]]:
        target = self._partial_resolve_ref(target)
        if isinstance(target, str):
            return self._resolve_store_data_for_simple_target(target, frame)
        (scope, obj, attr_or_sub, is_subscript) = self.node_id_to_saved_store_data.pop(
            target
        )
        if isinstance(obj, (dict, list)):
            # we can be reasonably sure that the object on the rhs is the same thing
            # that gets stashed in `obj` for these cases, so use it instead of doing
            # the lookup (which may have side effects) to reduce intrusiveness
            attr_or_sub_obj = self.saved_assign_rhs_obj
        else:
            attr_or_sub_obj = nbs().retrieve_namespace_attr_or_sub(
                obj, attr_or_sub, is_subscript
            )
        if attr_or_sub_obj is None:
            scope_to_use = scope
        else:
            scope_to_use = scope.get_earliest_ancestor_containing(
                id(attr_or_sub_obj), is_subscript
            )
        if scope_to_use is None:
            # Nobody before `scope` has it, so we'll insert it at this level
            scope_to_use = scope
        return (
            scope_to_use,
            attr_or_sub,
            attr_or_sub_obj,
            is_subscript,
            self.node_id_to_saved_live_subscript_refs.pop(target, set()),
        )

    def resolve_del_data_for_target(
        self, target: Union[str, int, ast.AST]
    ) -> Tuple[Scope, Optional[Any], AttrSubVal, bool]:
        target = self._partial_resolve_ref(target)
        if isinstance(target, str):
            return self.cur_frame_original_scope, None, target, False
        (scope, obj, attr_or_sub, is_subscript) = self.node_id_to_saved_del_data[target]
        return scope, obj, attr_or_sub, is_subscript

    def resolve_loaded_symbols(
        self, symbol_ref: Union[str, int, ast.AST, DataSymbol]
    ) -> List[DataSymbol]:
        if isinstance(symbol_ref, DataSymbol):
            return [symbol_ref]
        symbol_ref = self._partial_resolve_ref(symbol_ref)
        if isinstance(symbol_ref, int):
            return self.node_id_to_loaded_symbols.get(symbol_ref, [])
        elif isinstance(symbol_ref, str):
            ret = self.cur_frame_original_scope.lookup_data_symbol_by_name(symbol_ref)
            if ret is None:
                return []
            else:
                return [ret]
        else:
            return []

    def resolve_symbols(
        self, symbol_refs: Set[Union[str, int, DataSymbol]]
    ) -> Set[DataSymbol]:
        data_symbols = set()
        for ref in symbol_refs:
            data_symbols.update(self.resolve_loaded_symbols(ref))
        return data_symbols

    def _get_namespace_for_obj(
        self, obj: Any, obj_name: Optional[str] = None
    ) -> Namespace:
        obj_id = id(obj)
        ns = nbs().namespaces.get(obj_id, None)
        if ns is not None:
            return ns
        class_scope = nbs().namespaces.get(id(obj.__class__), None)
        if class_scope is not None:
            # logger.warning(
            #     'found class scope %s containing %s',
            #     class_scope, list(class_scope.all_data_symbols_this_indentation())
            # )
            ns = class_scope.clone(obj)
            if obj_name is not None:
                ns.scope_name = obj_name
        else:
            # print('no scope for class', obj.__class__)
            try:
                scope_name = (
                    nbs().get_first_full_symbol(obj_id).name
                    if obj_name is None
                    else obj_name
                )
            except AttributeError:
                scope_name = "<unknown namespace>"
            ns = Namespace(obj, scope_name, parent_scope=None)
        # FIXME: brittle strategy for determining parent scope of obj
        if ns.parent_scope is None:
            if (
                obj_name is not None
                and obj_name not in self.prev_trace_stmt_in_cur_frame.frame.f_locals
            ):
                parent_scope = nbs().global_scope
            else:
                parent_scope = self.active_scope
            ns.parent_scope = parent_scope
        return ns

    def _clear_info_and_maybe_lookup_or_create_complex_symbol(
        self, obj_attr_or_sub
    ) -> Optional[DataSymbol]:
        if self.saved_complex_symbol_load_data is None:
            return None
        (
            scope,
            obj,
            attr_or_subscript,
            is_subscript,
            *_,
        ) = self.saved_complex_symbol_load_data
        self.saved_complex_symbol_load_data = None
        data_sym = scope.lookup_data_symbol_by_name_this_indentation(
            attr_or_subscript,
            is_subscript=is_subscript,
            skip_cloned_lookup=True,
        )
        logger.warning("found sym %s in scope %s", data_sym, scope)
        if data_sym is None:
            parent = scope.lookup_data_symbol_by_name_this_indentation(
                attr_or_subscript,
                is_subscript,
                skip_cloned_lookup=False,
            )
            parents = set() if parent is None else {parent}
            is_default_dict = isinstance(obj, defaultdict)
            data_sym = scope.upsert_data_symbol_for_name(
                attr_or_subscript,
                obj_attr_or_sub,
                parents,
                self.prev_trace_stmt_in_cur_frame.stmt_node,
                is_subscript=is_subscript,
                propagate=is_default_dict,
                implicit=not is_default_dict,
            )
        elif data_sym.obj_id != id(obj_attr_or_sub):
            data_sym.update_obj_ref(obj_attr_or_sub)
        return data_sym

    @pyc.register_raw_handler(
        (
            pyc.before_call,
            pyc.before_attribute_load,
            pyc.before_attribute_store,
            pyc.before_attribute_del,
            pyc.before_subscript_load,
            pyc.before_subscript_store,
            pyc.before_subscript_del,
        )
    )
    def _save_node_id(self, _obj, node_id: NodeId, frame, *_, **__):
        self.prev_node_id_in_cur_frame = node_id
        self.prev_node_id_in_cur_frame_lexical = node_id

    # @pyc.register_raw_handler((pyc.before_for_loop_body, pyc.before_while_loop_body))
    # def before_loop_body(self, _obj: Any, loop_id: NodeId, *_, **__):
    #     ret = self.is_tracing_enabled and loop_id not in self._seen_loop_ids
    #     if ret:
    #         self._seen_loop_ids.add(loop_id)
    #     return ret

    @pyc.register_raw_handler((pyc.after_for_loop_iter, pyc.after_while_loop_iter))
    def after_loop_iter(self, _obj: Any, _loop_id: NodeId, *_, guard: str, **__):
        self.activate_guard(guard)

    # @pyc.register_raw_handler(pyc.after_function_execution)
    # def after_function_exec(self, _obj: Any, _loop_id: NodeId, *_, guard: str, **__):
    #     self.activate_guard(guard)

    @pyc.register_raw_handler(pyc.after_assign_rhs)
    @pyc.skip_when_tracing_disabled
    def after_assign_rhs(self, obj: Any, *_, **__):
        self.saved_assign_rhs_obj = obj

    @pyc.register_raw_handler(pyc.after_subscript_slice)
    @pyc.skip_when_tracing_disabled
    def after_subscript_slice(self, _obj: Any, node_id: NodeId, *__, **___):
        node = self.ast_node_by_id.get(node_id, None)
        if node is None:
            return
        slice_node = cast(ast.Subscript, node).slice
        live, _ = compute_live_dead_symbol_refs(
            slice_node, scope=self.cur_frame_original_scope
        )
        subscript_live_refs = []
        for ref in live:
            if len(ref.ref.chain) == 1:
                subscript_live_refs.append(cast(str, ref.ref.chain[0].value))
        self.node_id_to_saved_live_subscript_refs[node_id] = self.resolve_symbols(
            set(subscript_live_refs)
        )
        Timestamp.update_usage_info(
            self.cur_frame_original_scope.lookup_data_symbol_by_name(ref)
            for ref in subscript_live_refs
        )

    @pyc.register_raw_handler(
        (
            pyc.before_attribute_load,
            pyc.before_attribute_store,
            pyc.before_attribute_del,
            pyc.before_subscript_load,
            pyc.before_subscript_store,
            pyc.before_subscript_del,
        )
    )
    @pyc.skip_when_tracing_disabled
    def attrsub_tracer(
        self,
        obj: Any,
        node_id: NodeId,
        _frame_: FrameType,
        event: pyc.TraceEvent,
        *_,
        attr_or_subscript: AttrSubVal,
        call_context: bool,
        top_level_node_id: NodeId,
        obj_name: Optional[str] = None,
        **__,
    ):
        value_node_id = id(self.ast_node_by_id[node_id].value)  # type: ignore
        if isinstance(self.ast_node_by_id[value_node_id], ast.Call):
            # clear the callpoint dependency
            self.node_id_to_loaded_symbols.pop(value_node_id, None)
        if obj is None or obj is get_ipython():
            return
        logger.warning("%s %s of obj %s", event, attr_or_subscript, obj)
        sym_for_obj = self._clear_info_and_maybe_lookup_or_create_complex_symbol(obj)

        # Resolve symbol if necessary
        if sym_for_obj is None and obj_name is not None:
            sym_for_obj = self.active_scope.lookup_data_symbol_by_name_this_indentation(
                obj_name
            )

        scope = self._get_namespace_for_obj(obj, obj_name=obj_name)
        is_subscript = "subscript" in event.value
        if sym_for_obj is not None:
            try:
                data_sym = scope.lookup_data_symbol_by_name_this_indentation(
                    attr_or_subscript,
                    is_subscript=is_subscript,
                    skip_cloned_lookup=True,
                )
            except TypeError:
                data_sym = None
            if data_sym is None:
                sym_for_obj.update_usage_info()
            else:
                sym_for_obj.update_usage_info(exclude_ns=True)

        obj_id = id(obj)
        if self.top_level_node_id_for_chain is None:
            self.top_level_node_id_for_chain = top_level_node_id
        if self.first_obj_id_in_chain is None:
            self.first_obj_id_in_chain = obj_id

        try:
            if isinstance(attr_or_subscript, tuple):
                if not all(isinstance(v, (str, int)) for v in attr_or_subscript):
                    return
            elif not isinstance(attr_or_subscript, (str, int)):
                return
            if "store" in event.value:
                logger.warning(
                    "save store data for node id %d: %s, %s, %s, %s",
                    top_level_node_id,
                    scope,
                    obj,
                    attr_or_subscript,
                    is_subscript,
                )
                self.node_id_to_saved_store_data[top_level_node_id] = (
                    scope,
                    obj,
                    attr_or_subscript,
                    is_subscript,
                )
                return
            elif "del" in event.value:
                # logger.error("save del data for node %s", ast.dump(self.ast_node_by_id[top_level_node_id]))
                logger.warning("save del data for node id %d", top_level_node_id)
                self.node_id_to_saved_del_data[top_level_node_id] = (
                    scope,
                    obj,
                    attr_or_subscript,
                    is_subscript,
                )
                return
            logger.warning(
                "saved load data: %s, %s, %s", scope, attr_or_subscript, is_subscript
            )
            self.saved_complex_symbol_load_data = (
                scope,
                obj,
                attr_or_subscript,
                is_subscript,
                obj_name,
            )
            if call_context:
                if not is_subscript:
                    if (
                        sym_for_obj is None
                        and self.prev_trace_stmt_in_cur_frame is not None
                    ):
                        sym_for_obj = self.active_scope.upsert_data_symbol_for_name(
                            obj_name or "<anonymous_symbol_%d>" % id(obj),
                            obj,
                            set(),
                            self.prev_trace_stmt_in_cur_frame.stmt_node,
                            is_subscript=is_subscript,
                            is_anonymous=obj_name is None,
                            propagate=False,
                            implicit=True,
                        )
                    if sym_for_obj is not None:
                        assert self.top_level_node_id_for_chain is not None
                        self.node_id_to_loaded_symbols[
                            self.top_level_node_id_for_chain
                        ].append(sym_for_obj)
        finally:
            self.active_scope = scope

    def _process_possible_mutation(self, retval: Any) -> None:
        if self.mutation_candidate is None:
            return
        (
            (obj, obj_name, method_name),
            mutation_event,
            recorded_arg_dsyms,
            recorded_arg_objs,
        ) = self.mutation_candidate
        self.mutation_candidate = None
        if obj is logging or isinstance(obj, logging.Logger):
            # ignore calls to logging.whatever(...)
            return
        obj_type = None
        obj_id = id(obj)
        if obj_id in nbs().aliases:
            aliases = nbs().aliases[obj_id]
            if len(aliases) > 0:
                obj_type = next(iter(aliases)).obj_type
        if obj_type is None:
            obj_type = type(obj)
        is_excepted_mutation = False
        is_excepted_non_mutation = False
        if isinstance(mutation_event, StandardMutation):
            # only look for exceptions for standard mutations; other cases are handled elsewhere
            if retval is not None and id(retval) != obj_id:
                # doesn't look like something we can trace, but it also
                # doesn't look like something that mutates the caller, since
                # the return value is not None and it's not the caller object
                if (
                    obj_id,
                    method_name,
                ) in METHODS_WITH_MUTATION_EVEN_FOR_NON_NULL_RETURN:
                    is_excepted_mutation = True
                else:
                    return
            if not is_excepted_mutation:
                if retval is None:
                    is_excepted_non_mutation = (
                        obj_id,
                        method_name,
                    ) in METHODS_WITHOUT_MUTATION_EVEN_FOR_NULL_RETURN
                if (
                    is_excepted_non_mutation
                    or obj_type is None
                    or id(obj_type) in nbs().aliases
                ):
                    # the calling obj looks like something that we can trace;
                    # no need to process the call as a possible mutation
                    return
        arg_dsyms: Set[DataSymbol] = set()
        arg_dsyms = arg_dsyms.union(*recorded_arg_dsyms)
        if isinstance(mutation_event, StandardMutation):
            try:
                top_level_sym = nbs().get_first_full_symbol(self.first_obj_id_in_chain)
                if (
                    top_level_sym.is_import
                    and top_level_sym.name not in ARG_MUTATION_EXCEPTED_MODULES
                ):
                    # TODO: should it be the other way around?
                    #  i.e. allow-list for arg mutations, starting with np.random.seed?
                    mutated_dsym = None
                    if len(recorded_arg_dsyms) > 0:
                        first_arg_dsyms = list(recorded_arg_dsyms[0])
                        first_arg_dsyms = [
                            dsym
                            for dsym in first_arg_dsyms
                            if dsym.obj is recorded_arg_objs[0]
                        ]
                        if len(first_arg_dsyms) == 1:
                            mutated_dsym = first_arg_dsyms[0]
                            if mutated_dsym.obj_type in DataSymbol.IMMUTABLE_TYPES:
                                mutated_dsym = None
                            elif mutated_dsym.obj_type in {list, set, dict}:
                                # assume module code won't mutate these primitive containers
                                mutated_dsym = None
                    if mutated_dsym is not None:
                        # only make this an arg mutation event if it looks like there's an arg to mutate
                        arg_dsyms = {mutated_dsym}
                        # just consider the first one mutated unless other args depend on it
                        for other_recorded_arg_dsyms in recorded_arg_dsyms[1:]:
                            arg_dsyms.update(
                                {
                                    dsym
                                    for dsym in other_recorded_arg_dsyms
                                    if mutated_dsym in dsym.parents
                                }
                            )
                        mutation_event = ArgMutate()
            except:
                pass
        self.mutations.append((obj_id, mutation_event, arg_dsyms, recorded_arg_objs))

    @pyc.register_raw_handler(pyc.after_load_complex_symbol)
    def after_complex_symbol(self, obj: Any, *_, **__):
        try:
            if not self.is_tracing_enabled:
                return
            if self.first_obj_id_in_chain is None:
                return
            assert self.top_level_node_id_for_chain is not None
            loaded_sym = self._clear_info_and_maybe_lookup_or_create_complex_symbol(obj)
            if loaded_sym is not None:
                self.node_id_to_loaded_symbols[self.top_level_node_id_for_chain].append(
                    loaded_sym
                )
        finally:
            self.saved_complex_symbol_load_data = None
            self.first_obj_id_in_chain = None
            self.top_level_node_id_for_chain = None
            self.active_scope = self.cur_frame_original_scope

    @pyc.register_raw_handler(pyc.argument)
    @pyc.skip_when_tracing_disabled
    def argument(self, arg_obj: Any, arg_node_id: int, *_, **__):
        self.num_args_seen += 1
        arg_node = self.ast_node_by_id.get(arg_node_id, None)
        try:
            mut_cand = self.lexical_call_stack.get_field("mutation_candidate")
        except IndexError:
            return
        if mut_cand is None:
            return

        if (
            isinstance(mut_cand[1], (ListInsert, ListPop, ListRemove))
            and mut_cand[1].pos is None
            and self.num_args_seen == 1
        ):
            try:
                if isinstance(mut_cand[1], ListRemove):
                    mut_obj = mut_cand[0][0]
                    for i in range(len(mut_obj)):
                        if mut_obj[i] == arg_obj:
                            mut_cand[1].pos = i
                            break
                else:
                    mut_cand[1].pos = arg_obj
            except:
                pass

        if isinstance(arg_node, ast.Name):
            assert self.active_scope is self.cur_frame_original_scope
            arg_dsym = self.active_scope.lookup_data_symbol_by_name(arg_node.id)
            if arg_dsym is None:
                self.active_scope.upsert_data_symbol_for_name(
                    arg_node.id,
                    arg_obj,
                    set(),
                    self.prev_trace_stmt_in_cur_frame.stmt_node,
                    implicit=True,
                )
        mut_cand[-2].append(resolve_rval_symbols(arg_node))
        mut_cand[-1].append(arg_obj)

    def _save_mutation_candidate(
        self, obj: Any, method_name: Optional[str], obj_name: Optional[str] = None
    ) -> None:
        mutation_event = resolve_mutating_method(obj, method_name)
        if mutation_event is None or isinstance(
            mutation_event, MutatingMethodEventNotYetImplemented
        ):
            mutation_event = StandardMutation()
        self.mutation_candidate = ((obj, obj_name, method_name), mutation_event, [], [])

    @pyc.register_raw_handler(pyc.before_call)
    @pyc.skip_when_tracing_disabled
    def before_call(self, function_or_method, *_, **__):
        if self.saved_complex_symbol_load_data is None:
            obj, attr_or_subscript, is_subscript, obj_name = None, None, None, None
        else:
            # TODO: this will cause errors if we add more fields
            (
                _,
                obj,
                attr_or_subscript,
                is_subscript,
                *_,
                obj_name,
            ) = self.saved_complex_symbol_load_data
        if obj is not None and is_subscript is not None:
            if is_subscript:
                # TODO: need to do this also for chained calls, e.g. f()()
                method_name = None
            else:
                assert isinstance(attr_or_subscript, str)
                method_name = attr_or_subscript
                # method_name should match ast_by_id[function_or_method].func.id
            self._save_mutation_candidate(obj, method_name, obj_name=obj_name)
        self.saved_complex_symbol_load_data = None
        with self.lexical_call_stack.push():
            pass
        self.active_scope = self.cur_frame_original_scope

    @pyc.register_raw_handler((pyc.before_function_body, pyc.before_lambda_body))
    def before_function_body(self, _obj: Any, function_id: NodeId, *_, **__):
        ret = self.is_tracing_enabled and function_id not in self._seen_functions_ids
        if ret:
            self._seen_functions_ids.add(function_id)
        return ret

    @pyc.register_raw_handler(pyc.after_call)
    def after_call(
        self,
        retval: Any,
        _node_id: NodeId,
        frame: FrameType,
        *_,
        call_node_id: NodeId,
        **__,
    ):
        tracing_will_be_enabled_by_end = self.is_tracing_enabled
        if not self.is_tracing_enabled:
            tracing_will_be_enabled_by_end = self._should_attempt_to_reenable_tracing(
                frame
            )
            if tracing_will_be_enabled_by_end:
                # if tracing gets reenabled here instead of at the 'before_stmt' handler, then we're still
                # at the same module stmt as when tracing was disabled, and we still have a 'return' to trace
                self.call_depth = 1
                self.call_stack.clear()
                self.lexical_call_stack.clear()

        if not tracing_will_be_enabled_by_end:
            return

        # no need to reset active scope here;
        # that will happen in the 'after chain' handler

        if len(self.lexical_call_stack) > 0:
            # skip / give up if tracing was recently reenabled
            self.lexical_call_stack.pop()
        self.prev_node_id_in_cur_frame_lexical = None
        self._process_possible_mutation(retval)

        if not self.is_tracing_enabled:
            self._enable_tracing()

    # Note: we don't trace set literals
    @pyc.register_raw_handler(
        (
            pyc.before_dict_literal,
            pyc.before_list_literal,
            pyc.before_tuple_literal,
        )
    )
    @pyc.skip_when_tracing_disabled
    def before_literal(self, *_, **__):
        parent_scope = self.active_literal_scope or self.cur_frame_original_scope
        with self.lexical_literal_stack.push():
            self.active_literal_scope = Namespace(
                None, Namespace.ANONYMOUS, parent_scope
            )

    @pyc.register_raw_handler(
        (
            pyc.after_dict_literal,
            pyc.after_list_literal,
            pyc.after_tuple_literal,
        )
    )
    @pyc.skip_when_tracing_disabled
    def after_literal(
        self, literal: Union[dict, list, tuple], node_id: NodeId, *_, **__
    ):
        try:
            self.active_literal_scope.update_obj_ref(literal)
            logger.warning("create literal scope %s", self.active_literal_scope)
            starred_idx = -1
            starred_namespace = None
            outer_deps = set()
            for (i, inner_obj), (
                inner_key_node,
                inner_val_node,
            ) in match_container_obj_or_namespace_with_literal_nodes(
                literal, self.ast_node_by_id[node_id]  # type: ignore
            ):
                # TODO: memoize symbol resolution; otherwise this will be quadratic for deeply nested literals
                if isinstance(inner_val_node, ast.Starred):
                    inner_symbols = set()
                    starred_idx += 1
                    if starred_idx == 0:
                        starred_syms = self.resolve_loaded_symbols(inner_val_node)
                        starred_namespace = (
                            nbs().namespaces.get(starred_syms[0].obj_id, None)
                            if starred_syms
                            else None
                        )
                    if starred_namespace is not None:
                        starred_dep = starred_namespace.lookup_data_symbol_by_name_this_indentation(
                            starred_idx, is_subscript=True
                        )
                        inner_symbols.add(starred_dep)
                else:
                    inner_symbols = resolve_rval_symbols(inner_val_node)
                    if inner_key_node is not None:
                        outer_deps.update(resolve_rval_symbols(inner_key_node))
                self.node_id_to_loaded_symbols.pop(id(inner_val_node), None)
                inner_symbols.discard(None)
                if isinstance(
                    i, (int, str)
                ):  # TODO: perform more general check for SupportedIndexType
                    self.active_literal_scope.upsert_data_symbol_for_name(
                        i,
                        inner_obj,
                        inner_symbols,
                        self.prev_trace_stmt_in_cur_frame.stmt_node,
                        is_subscript=True,
                        implicit=True,
                        # this is necessary in case some literal object got reused,
                        # since as of this comment (2021/08/14) we do not clear
                        # GC'd symbols from the symbol graph
                        propagate=False,
                    )
            self.node_id_to_loaded_literal_scope[node_id] = self.active_literal_scope
            parent_scope: Scope = self.active_literal_scope.parent_scope
            assert parent_scope is not None
            literal_sym = parent_scope.upsert_data_symbol_for_name(
                "<literal_sym_%d>" % id(literal),
                literal,
                outer_deps,
                self.prev_trace_stmt_in_cur_frame.stmt_node,
                is_anonymous=True,
                implicit=True,
                propagate=False,
            )
            self.node_id_to_loaded_symbols[node_id].append(literal_sym)
            return literal
        finally:
            self.lexical_literal_stack.pop()

    @pyc.register_raw_handler(pyc.dict_key)
    @pyc.skip_when_tracing_disabled
    def dict_key(self, obj: Any, key_node_id: NodeId, *_, **__):
        self.node_id_to_saved_dict_key[key_node_id] = obj
        return obj

    @pyc.register_raw_handler(pyc.dict_value)
    @pyc.skip_when_tracing_disabled
    def dict_value(
        self,
        obj: Any,
        value_node_id: NodeId,
        *_,
        key_node_id: NodeId,
        dict_node_id: NodeId,
        **__,
    ):
        scope = self.node_id_to_loaded_literal_scope.pop(value_node_id, None)
        if scope is None:
            return obj
        # if we found a pending literal, assert that it's not dict unpacking
        assert key_node_id is not None
        key_obj = self.node_id_to_saved_dict_key.pop(key_node_id, None)
        if isinstance(key_obj, (str, int)):
            scope.scope_name = str(key_obj)
        return obj

    @pyc.register_raw_handler((pyc.list_elt, pyc.tuple_elt))
    @pyc.skip_when_tracing_disabled
    def list_or_tuple_elt(
        self,
        obj: Any,
        elt_node_id: NodeId,
        *_,
        index: Optional[int],
        container_node_id: NodeId,
        **__,
    ):
        scope = self.node_id_to_loaded_literal_scope.pop(elt_node_id, None)
        if scope is None:
            return obj
        if index is not None:
            scope.scope_name = str(index)
        return obj

    @pyc.register_raw_handler(pyc.after_lambda)
    @pyc.skip_when_tracing_disabled
    def after_lambda(self, obj: Any, lambda_node_id: int, frame: FrameType, *_, **__):
        sym_deps = []
        node = self.ast_node_by_id[lambda_node_id]
        for kw_default in node.args.defaults:  # type: ignore
            sym_deps.extend(self.resolve_loaded_symbols(kw_default))
        sym = self.active_scope.upsert_data_symbol_for_name(
            "<lambda_sym_%d>" % id(obj),
            obj,
            sym_deps,
            self.prev_trace_stmt_in_cur_frame.stmt_node,
            is_function_def=True,
            propagate=False,
        )
        # FIXME: this is super brittle. We're passing in a stmt node to update the mapping from
        #  stmt_node to function symbol, but simultaneously forcing the lambda symbol to hold
        #  a reference to the lambda in order to help with symbol resolution later
        sym.stmt_node = node
        self.node_id_to_loaded_symbols[lambda_node_id].append(sym)

    @pyc.register_raw_handler(pyc.after_stmt)
    def after_stmt(self, ret_expr: Any, stmt_id: int, frame: FrameType, *_, **__):
        if stmt_id in self.seen_stmts:
            return ret_expr
        self._saved_stmt_ret_expr = ret_expr
        stmt = self.ast_node_by_id.get(stmt_id, None)
        if stmt is not None:
            self.handle_other_sys_events(
                None, 0, frame, pyc.after_stmt, stmt_node=cast(ast.stmt, stmt)
            )
        return ret_expr

    @pyc.register_raw_handler(pyc.after_module_stmt)
    def after_module_stmt(self, *_, **__):
        if self.is_tracing_enabled:
            assert self.cur_frame_original_scope.is_global
        ret = self._saved_stmt_ret_expr
        self._saved_stmt_ret_expr = None
        self._module_stmt_counter += 1
        return ret

    @pyc.register_raw_handler(pyc.before_stmt)
    def before_stmt(self, _ret: None, stmt_id: int, frame: FrameType, *_, **__) -> None:
        self.next_stmt_node_id = stmt_id
        if stmt_id in self.seen_stmts:
            return
        # logger.warning('reenable tracing: %s', site_id)
        if self.prev_trace_stmt_in_cur_frame is not None:
            prev_trace_stmt_in_cur_frame = self.prev_trace_stmt_in_cur_frame
            # both of the following stmts should be processed when body is entered
            if isinstance(
                prev_trace_stmt_in_cur_frame.stmt_node, (ast.For, ast.If, ast.With)
            ):
                self.after_stmt(None, prev_trace_stmt_in_cur_frame.stmt_id, frame)
        trace_stmt = self.traced_statements.get(stmt_id, None)
        if trace_stmt is None:
            trace_stmt = TraceStatement(
                frame, cast(ast.stmt, self.ast_node_by_id[stmt_id])
            )
            self.traced_statements[stmt_id] = trace_stmt
        self.prev_trace_stmt_in_cur_frame = trace_stmt
        if not self.is_tracing_enabled and self._should_attempt_to_reenable_tracing(
            frame
        ):
            # At this point, we can be sure we're at the top level
            # because tracing was enabled in a top-level handler.
            # We also need to clear the stack, as we won't catch
            # the return event (since tracing was already disabled
            # when we got to a `before_stmt` event).
            self.call_depth = 0
            self.call_stack.clear()
            self.lexical_call_stack.clear()
            self.after_stmt_reset_hook()
            self._enable_tracing()

    def _should_attempt_to_reenable_tracing(self, frame: FrameType) -> bool:
        if nbs().is_develop:
            assert not self.is_tracing_enabled
            assert self.call_depth > 0, (
                "expected managed call depth > 0, got %d" % self.call_depth
            )
        call_depth = 0
        while frame is not None:
            if nbs().is_cell_file(frame.f_code.co_filename):
                call_depth += 1
            frame = frame.f_back
        if nbs().is_develop:
            assert call_depth >= 1, "expected call depth >= 1, got %d" % call_depth
        # TODO: allow reenabling tracing beyond just at the top level
        if call_depth != 1:
            return False
        if len(self.call_stack) == 0:
            stmt_in_top_level_frame = self.prev_trace_stmt_in_cur_frame
        else:
            stmt_in_top_level_frame = self.call_stack.get_field(
                "prev_trace_stmt_in_cur_frame", depth=0
            )
        if stmt_in_top_level_frame.finished:
            return False
        if nbs().trace_messages_enabled:
            self.EVENT_LOGGER.warning("reenable tracing >>>")
        return True

    def _get_or_make_trace_stmt(
        self, stmt_node: ast.stmt, frame: FrameType
    ) -> TraceStatement:
        trace_stmt = self.traced_statements.get(id(stmt_node), None)
        if trace_stmt is None:
            trace_stmt = TraceStatement(frame, stmt_node)
            self.traced_statements[id(stmt_node)] = trace_stmt
        return trace_stmt

    def _maybe_log_event(
        self, event: pyc.TraceEvent, stmt_node: ast.stmt, trace_stmt: TraceStatement
    ):
        if nbs().trace_messages_enabled:
            codeline = astunparse.unparse(stmt_node).strip("\n").split("\n")[0]
            codeline = " " * getattr(stmt_node, "col_offset", 0) + codeline
            self.EVENT_LOGGER.warning(
                " %3d: %10s >>> %s", trace_stmt.lineno, event, codeline
            )

    def _get_stmt_node_for_sys_event(
        self, event: pyc.TraceEvent, cell_num: int, lineno: int
    ) -> Optional[ast.stmt]:
        if event == pyc.return_ and self.next_stmt_node_id is not None:
            # this branch necessary for python < 3.8 where the frame
            # position maps to the calling location instead of the return
            return cast(ast.stmt, self.ast_node_by_id[self.next_stmt_node_id])
        try:
            stmt_node = self.stmt_by_lineno_by_module_id[cell_num][lineno]
            if event == pyc.call and not isinstance(
                stmt_node, (ast.AsyncFunctionDef, ast.FunctionDef)
            ):
                # TODO: this is bad and I should feel bad. Need a better way to figure out which
                #  stmt is executing than by using line numbers.
                parent_node = self.parent_stmt_by_id.get(id(stmt_node), None)
                if nbs().is_develop:
                    logger.info(
                        "node %s parent %s",
                        ast.dump(stmt_node),
                        None if parent_node is None else ast.dump(parent_node),
                    )
                if (
                    parent_node is not None
                    and getattr(parent_node, "lineno", None) == lineno
                    and isinstance(parent_node, (ast.AsyncFunctionDef, ast.FunctionDef))
                ):
                    stmt_node = parent_node
            return stmt_node
        except KeyError as e:
            if nbs().is_develop:
                self.EVENT_LOGGER.warning(
                    "got key error for stmt node in cell %d, line %d",
                    cell_num,
                    lineno,
                )
                raise e
        return None

    @pyc.register_raw_handler(pyc.call)
    def handle_call(
        self,
        ret_obj: Any,
        _node_id: None,
        frame: FrameType,
        event: pyc.TraceEvent,
        *_,
        **__,
    ):
        cell_num, lineno = nbs().get_position(frame)
        assert cell_num is not None
        stmt_node = self._get_stmt_node_for_sys_event(event, cell_num, lineno)
        trace_stmt = self._get_or_make_trace_stmt(stmt_node, frame)
        self._maybe_log_event(event, stmt_node, trace_stmt)

        try:
            prev_node_id_in_cur_frame_lexical = self.lexical_call_stack.get_field(
                "prev_node_id_in_cur_frame_lexical"
            )
        except IndexError:
            # this could happen if the call happens in library code,
            # and the corresponding notebook statement isn't an ast.Call
            # (e.g., it's a property or just induces a __repr__ call)
            # Make node_id_for_last_call point to self to cover such cases
            prev_node_id_in_cur_frame_lexical = id(stmt_node)

        if trace_stmt.node_id_for_last_call == prev_node_id_in_cur_frame_lexical:
            if nbs().trace_messages_enabled:
                self.EVENT_LOGGER.warning(" disable tracing >>>")
            self._disable_tracing()
            return pyc.Null
        trace_stmt.node_id_for_last_call = prev_node_id_in_cur_frame_lexical
        self.state_transition_hook(event, trace_stmt, ret_obj)

    @pyc.register_raw_handler((pyc.return_, pyc.exception))
    def handle_other_sys_events(
        self,
        ret_obj: Any,
        _node_id: None,
        frame: FrameType,
        event: pyc.TraceEvent,
        *_,
        stmt_node: Optional[ast.stmt] = None,
        **__,
    ):
        assert self.is_tracing_enabled or event == pyc.after_stmt

        cell_num, lineno = nbs().get_position(frame)
        assert cell_num is not None

        if event == pyc.after_stmt:
            assert stmt_node is not None
        else:
            stmt_node = self._get_stmt_node_for_sys_event(event, cell_num, lineno)

        trace_stmt = self._get_or_make_trace_stmt(stmt_node, frame)
        self._maybe_log_event(event, stmt_node, trace_stmt)
        self.state_transition_hook(event, trace_stmt, ret_obj)
