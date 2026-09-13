from graph import sales_graph 

def chat_with_sales_agent(
    message,
    thread_id
):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = sales_graph.invoke(
        {
            "query": message,
             "source": "chat"
        },
        config=config
    )

    return result.get(
        "response",
        "Sorry, I could not generate a response.")