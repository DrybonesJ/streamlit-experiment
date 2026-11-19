
import streamlit as st
import pandas as pd
from datetime import date

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EYARC | Accounting Lab",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SAMPLE DATA
# ============================================================

ACCOUNTS = {
    "Cash": {"type": "Asset"},
    "Accounts Receivable": {"type": "Asset"},
    "Supplies": {"type": "Asset"},
    "Equipment": {"type": "Asset"},
    "Accounts Payable": {"type": "Liability"},
    "Notes Payable": {"type": "Liability"},
    "Common Stock": {"type": "Equity"},
    "Service Revenue": {"type": "Revenue"},
    "Rent Expense": {"type": "Expense"},
    "Salaries Expense": {"type": "Expense"}
}

PROBLEMS = [
    {
        "id": 1,
        "title": "Owner Investment",
        "difficulty": "Beginner",
        "scenario": "The owner invests $8,000 cash in exchange for common stock.",
        "answer": {
            "Cash": (8000, 0),
            "Common Stock": (0, 8000)
        },
        "hint": "An asset increases and owners' equity increases.",
        "explanation": "Debit Cash and credit Common Stock."
    },
    {
        "id": 2,
        "title": "Purchase Equipment",
        "difficulty": "Beginner",
        "scenario": "The company purchases $2,500 of equipment on account.",
        "answer": {
            "Equipment": (2500, 0),
            "Accounts Payable": (0, 2500)
        },
        "hint": "Equipment increases, and the company owes the vendor.",
        "explanation": "Debit Equipment and credit Accounts Payable."
    },
    {
        "id": 3,
        "title": "Earn Service Revenue",
        "difficulty": "Beginner",
        "scenario": "The business earns $1,200 providing services for cash.",
        "answer": {
            "Cash": (1200, 0),
            "Service Revenue": (0, 1200)
        },
        "hint": "Cash increases and revenue increases.",
        "explanation": "Debit Cash and credit Service Revenue."
    },
    {
        "id": 4,
        "title": "Pay Monthly Rent",
        "difficulty": "Beginner",
        "scenario": "The company pays $950 cash for this month's rent.",
        "answer": {
            "Rent Expense": (950, 0),
            "Cash": (0, 950)
        },
        "hint": "Expenses normally increase with debits.",
        "explanation": "Debit Rent Expense and credit Cash."
    },
    {
        "id": 5,
        "title": "Collect Receivables",
        "difficulty": "Intermediate",
        "scenario": "A customer pays $1,600 toward an outstanding account receivable.",
        "answer": {
            "Cash": (1600, 0),
            "Accounts Receivable": (0, 1600)
        },
        "hint": "One asset increases while another decreases.",
        "explanation": "Debit Cash and credit Accounts Receivable."
    },
    {
        "id": 6,
        "title": "Bank Loan",
        "difficulty": "Intermediate",
        "scenario": "The company receives $5,000 cash after signing a bank note.",
        "answer": {
            "Cash": (5000, 0),
            "Notes Payable": (0, 5000)
        },
        "hint": "Borrowing money creates a liability, not revenue.",
        "explanation": "Debit Cash and credit Notes Payable."
    }
]

INITIAL_TRANSACTIONS = [
    {"date": "2026-11-01", "description": "Opening Investment", "account": "Cash", "debit": 12000.0, "credit": 0.0},
    {"date": "2026-11-01", "description": "Opening Investment", "account": "Common Stock", "debit": 0.0, "credit": 12000.0},
    {"date": "2026-11-03", "description": "Equipment Purchase", "account": "Equipment", "debit": 3000.0, "credit": 0.0},
    {"date": "2026-11-03", "description": "Equipment Purchase", "account": "Cash", "debit": 0.0, "credit": 3000.0},
    {"date": "2026-11-05", "description": "Client Services", "account": "Cash", "debit": 2400.0, "credit": 0.0},
    {"date": "2026-11-05", "description": "Client Services", "account": "Service Revenue", "debit": 0.0, "credit": 2400.0},
    {"date": "2026-11-07", "description": "Office Rent", "account": "Rent Expense", "debit": 800.0, "credit": 0.0},
    {"date": "2026-11-07", "description": "Office Rent", "account": "Cash", "debit": 0.0, "credit": 800.0}
]

# ============================================================
# SESSION STATE
# ============================================================

def default_entry():
    return pd.DataFrame([
        {"Account": "Cash", "Debit": 0.0, "Credit": 0.0},
        {"Account": "Common Stock", "Debit": 0.0, "Credit": 0.0}
    ])


if "transactions" not in st.session_state:
    st.session_state.transactions = [
        entry.copy() for entry in INITIAL_TRANSACTIONS
    ]

if "completed" not in st.session_state:
    st.session_state.completed = []

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "problem_id" not in st.session_state:
    st.session_state.problem_id = 1

if "journal_editor" not in st.session_state:
    st.session_state.journal_editor = default_entry()

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "company" not in st.session_state:
    st.session_state.company = "Nova Corp"

if "accent" not in st.session_state:
    st.session_state.accent = "#2563eb"

if "show_hints" not in st.session_state:
    st.session_state.show_hints = True


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):
    return f"${value:,.2f}"


def get_balances():
    df = pd.DataFrame(st.session_state.transactions)

    if df.empty:
        df = pd.DataFrame(
            columns=["account", "debit", "credit"]
        )

    grouped = df.groupby(
        "account", as_index=False
    )[["debit", "credit"]].sum()

    grouped["net_debit"] = (
        grouped["debit"] - grouped["credit"]
    )

    return grouped


def get_summary():
    balances = get_balances()

    net = dict(zip(
        balances["account"],
        balances["net_debit"]
    ))

    assets = sum(
        net.get(account, 0)
        for account, meta in ACCOUNTS.items()
        if meta["type"] == "Asset"
    )

    liabilities = -sum(
        net.get(account, 0)
        for account, meta in ACCOUNTS.items()
        if meta["type"] == "Liability"
    )

    contributed_equity = -sum(
        net.get(account, 0)
        for account, meta in ACCOUNTS.items()
        if meta["type"] == "Equity"
    )

    revenue = -sum(
        net.get(account, 0)
        for account, meta in ACCOUNTS.items()
        if meta["type"] == "Revenue"
    )

    expenses = sum(
        net.get(account, 0)
        for account, meta in ACCOUNTS.items()
        if meta["type"] == "Expense"
    )

    net_income = revenue - expenses

    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": contributed_equity + net_income,
        "revenue": revenue,
        "expenses": expenses,
        "net_income": net_income,
        "cash": net.get("Cash", 0)
    }


def reset_entry():
    st.session_state.journal_editor = default_entry()
    st.session_state.feedback = None


def check_entry(lines, problem):
    expected = problem["answer"]
    normalized = {}

    for _, row in lines.iterrows():
        account = str(row.get("Account", "")).strip()

        debit_value = pd.to_numeric(
            row.get("Debit", 0), errors="coerce"
        )
        credit_value = pd.to_numeric(
            row.get("Credit", 0), errors="coerce"
        )

        debit = 0.0 if pd.isna(debit_value) else float(debit_value)
        credit = 0.0 if pd.isna(credit_value) else float(credit_value)

        if debit < 0 or credit < 0:
            return False, "Amounts cannot be negative."

        if debit > 0 and credit > 0:
            return False, "A line cannot contain both a debit and credit."

        if debit == 0 and credit == 0:
            continue

        if account not in ACCOUNTS:
            return False, f"Unknown account: {account}"

        if account not in normalized:
            normalized[account] = [0.0, 0.0]

        normalized[account][0] += debit
        normalized[account][1] += credit

    total_debits = sum(
        values[0] for values in normalized.values()
    )

    total_credits = sum(
        values[1] for values in normalized.values()
    )

    if total_debits <= 0:
        return False, "Enter a journal entry first."

    if abs(total_debits - total_credits) > 0.005:
        return False, "Debits and credits must balance."

    if set(normalized) != set(expected):
        return False, "One or more accounts are incorrect."

    for account, (debit, credit) in expected.items():
        actual = normalized[account]

        if (
            abs(actual[0] - debit) > 0.005
            or abs(actual[1] - credit) > 0.005
        ):
            return False, "Check your amounts and debit/credit sides."

    return True, problem["explanation"]


# ============================================================
# CUSTOM CSS
# ============================================================

accent = st.session_state.accent

st.markdown(
    f"""
    <style>
        .block-container {{
            max-width: 1350px;
            padding-top: 1.5rem;
        }}

        [data-testid="stMetric"] {{
            border: 1px solid #dfe6ef;
            padding: 18px;
            border-radius: 14px;
        }}

        .eyarc-hero {{
            background: linear-gradient(110deg, #0b2248, #143b72);
            padding: 30px;
            border-radius: 18px;
            margin-bottom: 22px;
            color: white;
        }}

        .eyarc-hero h1 {{
            color: white;
            margin: 0;
            font-size: 2.2rem;
        }}

        .eyarc-hero p {{
            color: #dbeafe;
            margin: 10px 0 0;
        }}

        .eyarc-pill {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 100px;
            background: {accent};
            color: white;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 12px;
        }}

        div.stButton > button[kind="primary"] {{
            background: {accent};
            border-color: {accent};
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("📘 EYARC")
    st.caption("Accounting Lab")
    st.divider()

    st.subheader("Settings")

    st.text_input(
        "Company Name",
        key="company"
    )

    st.toggle(
        "Show Exercise Hints",
        key="show_hints"
    )

    st.selectbox(
        "Accent Color",
        [
            "#2563eb",
            "#0d9488",
            "#85428e",
            "#ea580c"
        ],
        format_func=lambda color: {
            "#2563eb": "Blue",
            "#0d9488": "Teal",
            "#85428e": "Purple",
            "#ea580c": "Orange"
        }[color],
        key="accent"
    )

    st.divider()

    if st.button(
        "Reset Demo Data",
        use_container_width=True
    ):
        st.session_state.transactions = [
            entry.copy() for entry in INITIAL_TRANSACTIONS
        ]
        st.session_state.completed = []
        st.session_state.attempts = 0
        st.session_state.problem_id = 1
        reset_entry()

        for key in list(st.session_state):
            if key.startswith("editor_"):
                del st.session_state[key]

        st.rerun()

    st.caption(
        "Demo data is stored in your current session."
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="eyarc-hero">
        <span class="eyarc-pill">INTERACTIVE DEMO</span>
        <h1>Accounting Lab</h1>
        <p>
            Practice journal entries, inspect financial
            statements, and experiment with a live ledger.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

tab_overview, tab_practice, tab_ledger, tab_reports, tab_about = st.tabs([
    "📊 Overview",
    "✍️ Practice",
    "📒 Ledger",
    "📈 Financial Reports",
    "⚙️ About"
])


# ============================================================
# OVERVIEW TAB
# ============================================================

with tab_overview:

    st.subheader(
        f"{st.session_state.company} Dashboard"
    )

    summary = get_summary()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Cash Balance",
        money(summary["cash"])
    )

    col2.metric(
        "Revenue",
        money(summary["revenue"])
    )

    col3.metric(
        "Expenses",
        money(summary["expenses"])
    )

    col4.metric(
        "Net Income",
        money(summary["net_income"])
    )

    st.divider()

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("#### Financial Position")

        comparison = pd.DataFrame({
            "Amount": [
                summary["assets"],
                summary["liabilities"],
                summary["equity"]
            ]
        }, index=[
            "Assets",
            "Liabilities",
            "Equity"
        ])

        st.bar_chart(
            comparison,
            horizontal=True
        )

        st.caption(
            "Assets should equal liabilities plus equity."
        )

    with right:
        st.markdown("#### Student Progress")

        completed = len(st.session_state.completed)
        total = len(PROBLEMS)

        st.progress(
            completed / total,
            text=f"{completed} of {total} problems completed"
        )

        st.metric(
            "Submission Attempts",
            st.session_state.attempts
        )

        st.markdown("#### Recent Activity")

        transactions = pd.DataFrame(
            st.session_state.transactions
        )

        st.dataframe(
            transactions.tail(6)[[
                "description",
                "account",
                "debit",
                "credit"
            ]],
            hide_index=True,
            use_container_width=True
        )


# ============================================================
# JOURNAL ENTRY PRACTICE TAB
# ============================================================

with tab_practice:

    st.subheader("Journal Entry Practice")

    selected_id = st.selectbox(
        "Select a Problem",
        [problem["id"] for problem in PROBLEMS],
        format_func=lambda problem_id: (
            f"{problem_id}. "
            + next(
                p["title"]
                for p in PROBLEMS
                if p["id"] == problem_id
            )
        ),
        key="problem_id",
        on_change=reset_entry
    )

    problem = next(
        p for p in PROBLEMS
        if p["id"] == selected_id
    )

    st.caption(
        f"Difficulty: {problem['difficulty']}"
    )

    st.info(
        problem["scenario"],
        icon="🧩"
    )

    if st.session_state.show_hints:
        with st.expander("Need a Hint?"):
            st.write(problem["hint"])

    st.markdown("#### Prepare the Journal Entry")

    st.caption(
        "Select accounts and enter debit and credit amounts."
    )

    editor_key = f"editor_{selected_id}"

    edited = st.data_editor(
        st.session_state.journal_editor,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Account": st.column_config.SelectboxColumn(
                "Account",
                options=list(ACCOUNTS.keys()),
                required=True
            ),
            "Debit": st.column_config.NumberColumn(
                "Debit",
                min_value=0,
                step=100.0,
                format="$%.2f"
            ),
            "Credit": st.column_config.NumberColumn(
                "Credit",
                min_value=0,
                step=100.0,
                format="$%.2f"
            )
        },
        key=editor_key
    )

    total_debits = float(
        pd.to_numeric(
            edited["Debit"],
            errors="coerce"
        ).fillna(0).sum()
    )

    total_credits = float(
        pd.to_numeric(
            edited["Credit"],
            errors="coerce"
        ).fillna(0).sum()
    )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Total Debits",
        money(total_debits)
    )

    metric2.metric(
        "Total Credits",
        money(total_credits)
    )

    metric3.metric(
        "Difference",
        money(abs(total_debits - total_credits))
    )

    submit_col, clear_col = st.columns(2)

    if submit_col.button(
        "Check My Entry",
        type="primary",
        use_container_width=True
    ):

        st.session_state.attempts += 1

        correct, message = check_entry(
            edited,
            problem
        )

        st.session_state.feedback = (
            correct,
            message,
            selected_id
        )

        if (
            correct
            and selected_id not in st.session_state.completed
        ):

            st.session_state.completed.append(
                selected_id
            )

            for account, amounts in problem["answer"].items():

                debit, credit = amounts

                st.session_state.transactions.append({
                    "date": date.today().isoformat(),
                    "description": (
                        f"Exercise {selected_id}: "
                        f"{problem['title']}"
                    ),
                    "account": account,
                    "debit": float(debit),
                    "credit": float(credit)
                })

    if clear_col.button(
        "Clear Answer",
        use_container_width=True
    ):
        reset_entry()
        st.session_state.pop(editor_key, None)
        st.rerun()

    if st.session_state.feedback is not None:

        correct, message, feedback_problem = (
            st.session_state.feedback
        )

        if feedback_problem == selected_id:
            if correct:
                st.success(
                    f"Correct! {message} "
                    "Your entry has been posted to the ledger."
                )
            else:
                st.error(message)

    if selected_id in st.session_state.completed:
        st.caption(
            "✅ Completed — this entry has already been posted."
        )


# ============================================================
# GENERAL LEDGER TAB
# ============================================================

with tab_ledger:

    st.subheader("General Ledger")

    transactions = pd.DataFrame(
        st.session_state.transactions
    )

    selected_accounts = st.multiselect(
        "Filter Accounts",
        options=list(ACCOUNTS.keys())
    )

    if selected_accounts:
        filtered = transactions[
            transactions["account"].isin(
                selected_accounts
            )
        ]
    else:
        filtered = transactions

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "debit": st.column_config.NumberColumn(
                "Debit",
                format="$%.2f"
            ),
            "credit": st.column_config.NumberColumn(
                "Credit",
                format="$%.2f"
            )
        }
    )

    st.download_button(
        "Download Ledger CSV",
        data=transactions.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="eyarc_general_ledger.csv",
        mime="text/csv"
    )

    st.divider()

    st.markdown("### Trial Balance")

    balances = get_balances()

    balances["Debit Balance"] = (
        balances["net_debit"].clip(lower=0)
    )

    balances["Credit Balance"] = (
        (-balances["net_debit"]).clip(lower=0)
    )

    st.dataframe(
        balances[[
            "account",
            "Debit Balance",
            "Credit Balance"
        ]],
        use_container_width=True,
        hide_index=True
    )

    debit_total = balances["Debit Balance"].sum()
    credit_total = balances["Credit Balance"].sum()

    st.write(
        f"**Total Debits:** {money(debit_total)}"
    )

    st.write(
        f"**Total Credits:** {money(credit_total)}"
    )

    if abs(debit_total - credit_total) < 0.005:
        st.success(
            "The trial balance is balanced."
        )
    else:
        st.warning(
            "The trial balance does not balance."
        )


# ============================================================
# FINANCIAL REPORTS TAB
# ============================================================

with tab_reports:

    st.subheader("Financial Reports")

    summary = get_summary()

    report_type = st.radio(
        "Select Report",
        [
            "Income Statement",
            "Balance Sheet"
        ],
        horizontal=True
    )

    st.markdown(
        f"#### {st.session_state.company}"
    )

    if report_type == "Income Statement":

        st.markdown("### Income Statement")

        income_data = pd.DataFrame([
            {
                "Line Item": "Service Revenue",
                "Amount": summary["revenue"]
            },
            {
                "Line Item": "Less: Expenses",
                "Amount": -summary["expenses"]
            },
            {
                "Line Item": "Net Income",
                "Amount": summary["net_income"]
            }
        ])

        st.table(income_data)

        st.bar_chart(
            income_data.set_index("Line Item")
        )

    else:

        st.markdown("### Balance Sheet")

        balance_data = pd.DataFrame([
            {
                "Line Item": "Total Assets",
                "Amount": summary["assets"]
            },
            {
                "Line Item": "Total Liabilities",
                "Amount": summary["liabilities"]
            },
            {
                "Line Item": "Total Equity",
                "Amount": summary["equity"]
            },
            {
                "Line Item": "Liabilities + Equity",
                "Amount": (
                    summary["liabilities"]
                    + summary["equity"]
                )
            }
        ])

        st.table(balance_data)

        difference = (
            summary["assets"]
            - summary["liabilities"]
            - summary["equity"]
        )

        if abs(difference) < 0.005:
            st.success(
                "Assets = Liabilities + Equity"
            )
        else:
            st.warning(
                "The accounting equation does not balance."
            )

    st.caption(
        "These are simplified educational financial reports."
    )


# ============================================================
# ABOUT / TESTING TAB
# ============================================================

with tab_about:

    st.subheader("Deployment Testing")

    st.write(
        "This application is designed to help you "
        "experiment with Streamlit development."
    )

    st.markdown("### Changes to Try")

    st.markdown("""
    1. Change the title of the application.
    2. Add another accounting problem.
    3. Add a new account to the chart of accounts.
    4. Change the colors in the CSS.
    5. Add another dashboard metric.
    6. Create another tab.
    7. Modify the financial statement calculations.
    """)

    st.divider()

    st.markdown("### Deploying Updates")

    st.code(
        'git add .\n'
        'git commit -m "Update EYARC Demo"\n'
        'git push',
        language="powershell"
    )

    st.info(
        "After pushing to GitHub, Streamlit Community "
        "Cloud will redeploy your updated application."
    )

    st.warning(
        "Student progress is currently stored in "
        "session state rather than a permanent database."
    )
