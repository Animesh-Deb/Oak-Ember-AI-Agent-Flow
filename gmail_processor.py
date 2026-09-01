import time 
from gmail_services import ( 
    get_gmail_service,
    get_unread_emails,
    get_email,
    extract_email_information,
    send_email_reply,
    mark_as_read,
    recommendation_to_html
) 
from graph import sales_graph 
from email.utils import parseaddr
# ============================================================ 
# EMAIL ADDRESS EXTRACTION 
# ============================================================ 
 
def extract_email_address(sender): 
 
    if "<" in sender and ">" in sender: 
 
        return ( 
            sender 
            .split("<")[1] 
            .split(">")[0] 
            .strip() 
        ) 
 
    return sender.strip() 
 
 
# ============================================================ 
# BUILD CUSTOMER EMAIL 
# ============================================================ 
 
def build_customer_email(result):

    recommendation = result.get("recommendation")
    plain_response = result.get("response")

    # ------------------------------------------------------
    # CASE 1: We have a structured recommendation -> table
    # ------------------------------------------------------
    if recommendation:

        recommendation_html = recommendation_to_html(
            recommendation
        )
        # recommendation_to_html already returns a full
        # <html><body>...</body></html> document (summary,
        # table, verify-price note, sign-off) - send it as-is,
        # do NOT wrap it in another <html> document.
        return recommendation_html

    # ------------------------------------------------------
    # CASE 2: No recommendation, but a node produced a
    # specific message (clarification, no-match, blocked,
    # unsubscribe, insufficient info) -> use it, don't
    # replace it with a generic fallback.
    # ------------------------------------------------------
    if plain_response:

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">

            <p>Hello,</p>

            <p>{plain_response}</p>

            <p>
            Thank you,<br>
            <strong>Oak &amp; Ember Interiors</strong>
            </p>

        </body>
        </html>
        """

    # ------------------------------------------------------
    # CASE 3: Truly nothing to say (shouldn't normally happen)
    # ------------------------------------------------------
    return """
    <html>
    <body style="font-family: Arial, sans-serif;">

    <p>Hello,</p>

    <p>
    Thank you for contacting <strong>Oak &amp; Ember Interiors</strong>.
    We were unable to process your request at this time. Please try again.
    </p>

    <p>
    Thank you,<br>
    Oak &amp; Ember Interiors
    </p>

    </body>
    </html>
    """
 
# ============================================================ 
# PROCESS ONE EMAIL 
# ============================================================ 
 
def process_email( 
    service, 
    message_id 
): 
 
    email = get_email( 
        service, 
        message_id 
    ) 
 
    email_info = extract_email_information( 
        email 
    ) 
 
    sender = extract_email_address( 
        email_info["sender"] 
    ) 
 
    subject = email_info["subject"] 
    body = email_info["body"] 
 
    gmail_thread_id = email_info[ 
        "thread_id" 
    ] 
 
    print("\n" + "=" * 70) 
    print("NEW CUSTOMER EMAIL") 
    print("=" * 70) 
 
    print("Sender:", sender) 
    print("Subject:", subject) 
    print("Thread:", gmail_thread_id) 
 
    print("\nCustomer message:") 
    print(body) 
 
    # ======================================================== 
    # USE SAME GRAPH + MEMORY 
    # ======================================================== 
 
    graph_thread_id = ( 
        f"gmail_{gmail_thread_id}" 
    ) 
 
    result = sales_graph.invoke( 
 
        { 
            "query": body, 
            "source": "email",
            "email": sender
        },
        config={ 
            "configurable": { 
                "thread_id": graph_thread_id 
            } 
        } 
    ) 
 
    print("\nGraph response:") 
    print( 
        result.get( 
            "response", 
            "" 
        ) 
    ) 
 
    # ======================================================== 
    # FORMAT EMAIL 
    # ======================================================== 
 
    reply_body = build_customer_email( 
        result 
    ) 
 
    if subject.lower().startswith("re:"): 
 
        reply_subject = subject 
 
    else: 
 
        reply_subject = ( 
            "Re: " + subject 
        ) 
 
    # ======================================================== 
    # SEND EMAIL 
    # ======================================================== 
 
    send_email_reply( 
 
        service=service, 
 
        recipient=sender, 
 
        subject=reply_subject, 
 
        body=reply_body, 
 
        thread_id=gmail_thread_id 
    ) 
 
    print("\nReply sent to:", sender) 
 
    # ======================================================== 
    # MARK ORIGINAL EMAIL AS READ 
    # ======================================================== 
 
    mark_as_read( 
        service, 
        message_id 
    ) 
 
    print("Original email marked as read.") 
 
 
# ============================================================ 
# CHECK GMAIL 
# ============================================================ 
 
def check_gmail(service): 
 
    messages = get_unread_emails( 
        service, 
        max_results=10 
    ) 
 
    if not messages: 
 
        print( 
            "No new emails." 
        ) 
 
        return 
 
    print( 
        f"Found {len(messages)} unread email(s)." 
    ) 
 
    for message in messages: 
 
        try: 
 
            process_email( 
                service, 
                message["id"] 
            ) 
 
        except Exception as e: 
 
            print( 
                "\nERROR processing email:" 
            ) 
 
            print(e) 
 
 
# ============================================================ 
# CONTINUOUS GMAIL WORKER 
# ============================================================ 
 
def run_gmail_worker(): 
 
    print("\n" + "=" * 70) 
    print("OAK & EMBER GMAIL WORKER") 
    print("=" * 70) 
 
    print( 
        "Gmail worker started." 
    ) 
 
    print( 
        "Waiting for new customer emails..." 
    ) 
 
    print( 
        "Press CTRL+C to stop." 
    ) 
 
    # Authenticate once 
    service = get_gmail_service() 
 
    # ======================================================== 
    # CONTINUOUS LOOP 
    # ======================================================== 
 
    while True: 
 
        try: 
 
            print( 
                "\nChecking Gmail..." 
            ) 
 
            check_gmail( 
                service 
            ) 
 
        except Exception as e: 
 
            print( 
                "\nGmail worker error:" 
            ) 
 
            print(e) 
 
        # ==================================================== 
        # WAIT BEFORE NEXT CHECK 
        # ==================================================== 
 
        print( 
            "\nWaiting 15 seconds..." 
        ) 
 
        time.sleep(15) 
 
 
# ============================================================ 
# START WORKER 
# ============================================================ 
 
if __name__ == "__main__": 
 
    try: 
 
        run_gmail_worker() 
 
    except KeyboardInterrupt: 
 
        print( 
            "\nGmail worker stopped." 
        )