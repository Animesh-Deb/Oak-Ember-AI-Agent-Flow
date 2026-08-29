from state import SalesState
from AIguardrail import check_input_guardrail


# Guardrail node
def guardrail_node(state: SalesState):

    query = state["query"]

    result = check_input_guardrail(query)

    print("\n" + "=" * 50)
    print("GUARDRAIL RESULT:")
    print(result.model_dump())
    print("=" * 50)

    return {
        "guardrail_result": result.model_dump()
    }