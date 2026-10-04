from support_ops.agent.state import AgentState, AgentStatus, ToolExecution
from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
    IncomingTicket,
)
from support_ops.llm import LLMClient
from support_ops.memory.manager import MemoryManager
from support_ops.tools.registry import ToolRegistry


class SupportAgent:
    def __init__(
        self,
        llm: LLMClient,
        tools: ToolRegistry,
        memory: MemoryManager,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.memory = memory

    def build_context(
        self,
        state: AgentState,
    ) -> str:

        customer_memory = self.memory.get_customer(state.ticket.customer_id)

        tool_history = "\n".join(
            f"""
Tool: {execution.tool_name}
Arguments: {execution.arguments}
Success: {execution.success}
Result: {execution.result}
Data: {execution.data}
"""
            for execution in state.tool_calls
        )

        return f"""
Ticket:
Customer ID: {state.ticket.customer_id}
Subject: {state.ticket.subject}
Description: {state.ticket.description}

Customer memory:
{customer_memory.model_dump_json()}

Previous tool executions:
{tool_history}

Current iteration:
{state.iteration}
"""

    def decide(
        self,
        state: AgentState,
    ) -> AgentDecision:

        context = self.build_context(state)

        prompt = f"""
You are a support operations agent.

Analyze the current state and decide the next action.

Available actions:

- search_knowledge_base
- draft_response
- create_ticket
- escalate

You may perform another action if more information is required.

{context}

Rules:

- Use search_knowledge_base and create_ticket only together with
  tool_name and tool_arguments.
- Use draft_response when you have enough information to answer the
  customer, and put the customer-facing answer in response.
- Use escalate when a human must take over.

Return JSON with exactly these fields:

{{
  "action": "search_knowledge_base|draft_response|create_ticket|escalate",
  "reason": "short explanation",
  "tool_name": "tool to run, or null when no tool is needed",
  "tool_arguments": {{}},
  "response": "customer-facing answer, or null unless drafting"
}}
"""

        return self.llm.structured(
            prompt,
            AgentDecision,
        )

    def execute_decision(
        self,
        state: AgentState,
        decision: AgentDecision,
    ) -> None:

        if decision.tool_name is None:
            state.status = AgentStatus.FAILED
            state.error = "Tool action requires a tool name."
            return

        try:
            tool = self.tools.get(decision.tool_name)

            schema = tool.argument_schema()

            arguments = schema.model_validate(decision.tool_arguments)
        except ValueError as error:
            state.status = AgentStatus.FAILED
            state.error = f"Could not run tool {decision.tool_name!r}: {error}"
            return

        result = tool.execute(arguments)

        execution = ToolExecution(
            tool_name=decision.tool_name,
            arguments=decision.tool_arguments,
            success=result.success,
            result=result.message,
            data=result.data,
        )

        state.tool_calls.append(execution)

        self.memory.remember_message(
            role="tool",
            content=result.message,
        )

    def run(
        self,
        ticket: IncomingTicket,
    ) -> AgentState:

        self.memory.remember_message(
            role="user",
            content=ticket.description,
        )

        state = AgentState(ticket=ticket)

        while state.status == AgentStatus.RUNNING:
            state.iteration += 1

            if state.iteration > state.max_iterations:
                state.status = AgentStatus.MAX_ITERATIONS
                break

            decision = self.decide(state)

            if decision.action == AgentAction.DRAFT_RESPONSE:
                state.final_response = decision.response or decision.reason
                state.status = AgentStatus.COMPLETED
                break

            if decision.action == AgentAction.ESCALATE:
                state.final_response = (
                    "This issue requires escalation to a human support agent."
                )
                state.status = AgentStatus.COMPLETED
                break

            self.execute_decision(
                state,
                decision,
            )

        return state
