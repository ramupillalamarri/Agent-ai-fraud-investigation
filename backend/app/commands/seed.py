import argparse
import asyncio
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.database.database import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.models.investigation import Investigation
from app.models.agent_result import AgentResult
from app.models.evidence import Evidence
from app.models.recommendation import Recommendation
from app.models.timeline_event import TimelineEvent


async def _seed_exec(
    db: AsyncSession,
    admin_email: str,
    admin_password: str,
    analyst_email: str,
    analyst_password: str,
    reset: bool = False,
) -> None:
    """Internal implementation executing database seeding."""
    # ==========================================
    # 1. Reset Database Records (if requested)
    # ==========================================
    if reset:
        print("Resetting database tables...")
        await db.execute(delete(RefreshToken))
        await db.execute(delete(AuditLog))
        await db.execute(delete(TimelineEvent))
        await db.execute(delete(Recommendation))
        await db.execute(delete(Evidence))
        await db.execute(delete(AgentResult))
        await db.execute(delete(Investigation))
        await db.execute(delete(User))
        await db.execute(delete(Role))
        await db.execute(delete(Permission))
        await db.commit()
        print("Database reset complete.")

    # ==========================================
    # 2. Seed Roles
    # ==========================================
    roles_to_seed = [
        ("Admin", "Super user with full operational authorization."),
        ("Fraud Analyst", "Core user role for retail transaction and alert analysis."),
    ]

    seeded_roles = {}
    for role_name, role_desc in roles_to_seed:
        res = await db.execute(select(Role).where(Role.name == role_name))
        role = res.scalars().first()
        if not role:
            role = Role(name=role_name, description=role_desc)
            role.permissions = []
            db.add(role)
        seeded_roles[role_name] = role

    # ==========================================
    # 3. Seed Permissions
    # ==========================================
    permissions_to_seed = [
        ("users:create", "Ability to create new system user accounts."),
        ("users:delete", "Ability to delete or soft-delete system user accounts."),
        ("dashboard:view", "Ability to view the main intelligence dashboard."),
        ("fraud:investigate", "Ability to triage transactions and investigate fraud cases."),
        ("reports:generate", "Ability to generate and export analytics reports."),
        ("investigation:read", "Ability to view investigations."),
        ("investigation:write", "Ability to execute/create investigations."),
        ("investigation:update", "Ability to edit/update investigations."),
        ("investigation:delete", "Ability to delete investigations."),
    ]

    seeded_permissions = {}
    for perm_name, perm_desc in permissions_to_seed:
        res = await db.execute(select(Permission).where(Permission.name == perm_name))
        perm = res.scalars().first()
        if not perm:
            perm = Permission(name=perm_name, description=perm_desc)
            db.add(perm)
        seeded_permissions[perm_name] = perm

    # Flush to generate IDs before mapping
    await db.flush()

    # ==========================================
    # 4. Map Permissions to Roles
    # ==========================================
    # Admin gets all permissions
    for perm in seeded_permissions.values():
        if perm not in seeded_roles["Admin"].permissions:
            seeded_roles["Admin"].permissions.append(perm)
            db.add(seeded_roles["Admin"])

    # Fraud Analyst gets dashboard:view, fraud:investigate, reports:generate, etc.
    analyst_perms = [
        seeded_permissions["dashboard:view"],
        seeded_permissions["fraud:investigate"],
        seeded_permissions["reports:generate"],
        seeded_permissions["investigation:read"],
        seeded_permissions["investigation:write"],
        seeded_permissions["investigation:update"],
    ]
    for perm in analyst_perms:
        if perm not in seeded_roles["Fraud Analyst"].permissions:
            seeded_roles["Fraud Analyst"].permissions.append(perm)
            db.add(seeded_roles["Fraud Analyst"])

    # ==========================================
    # 5. Seed Users
    # ==========================================
    # Seed Admin User
    res = await db.execute(select(User).where(User.email == admin_email))
    admin_user = res.scalars().first()
    if not admin_user:
        hashed_pwd = security.get_password_hash(admin_password)
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_pwd,
            full_name="Default System Administrator",
            is_active=True,
        )
        admin_user.roles.append(seeded_roles["Admin"])
        db.add(admin_user)
        print(f"Admin user seeded successfully ({admin_email}).")
    else:
        print(f"Admin user ({admin_email}) already exists. Skipping.")

    # Seed Fraud Analyst User
    res = await db.execute(select(User).where(User.email == analyst_email))
    analyst_user = res.scalars().first()
    if not analyst_user:
        hashed_pwd = security.get_password_hash(analyst_password)
        analyst_user = User(
            email=analyst_email,
            hashed_password=hashed_pwd,
            full_name="Default Fraud Analyst",
            is_active=True,
        )
        analyst_user.roles.append(seeded_roles["Fraud Analyst"])
        db.add(analyst_user)
        print(f"Fraud Analyst user seeded successfully ({analyst_email}).")
    else:
        print(f"Fraud Analyst user ({analyst_email}) already exists. Skipping.")

    # ==========================================================
    # 6. Seed Investigations, Transactions, Customers & Merchants
    # ==========================================================
    print("Generating E2E demo dataset (100 Transactions/Investigations)...")
    
    customers = [f"CUST-{i:04d}" for i in range(1001, 1021)]  # 20 Customers
    merchants = [f"MERCH-{i:04d}" for i in range(2001, 2016)]  # 15 Merchants
    categories = ["retail", "electronics", "groceries", "travel", "entertainment"]
    countries = ["US", "US", "CA", "GB", "DE", "FR", "JP"]
    payment_methods = ["credit", "debit", "paypal", "apple_pay"]
    device_types = ["mobile", "desktop", "tablet"]

    investigation_objects = []
    
    for i in range(100):
        # Evenly spread scores to fully exercise dashboard buckets
        if i < 15:
            # Critical risk bucket (15 items)
            risk_score = random.randint(80, 100)
            priority = "HIGH"
            fraud_prob = round(risk_score / 100.0, 4)
            status = random.choice(["PENDING", "RUNNING", "ESCALATED"])
        elif i < 40:
            # High risk bucket (25 items)
            risk_score = random.randint(60, 79)
            priority = "HIGH"
            fraud_prob = round(risk_score / 100.0, 4)
            status = random.choice(["PENDING", "RUNNING", "COMPLETED", "RESOLVED"])
        elif i < 70:
            # Medium risk bucket (30 items)
            risk_score = random.randint(40, 59)
            priority = "MEDIUM"
            fraud_prob = round(risk_score / 100.0, 4)
            status = random.choice(["COMPLETED", "RESOLVED", "CLOSED"])
        else:
            # Low risk bucket (30 items)
            risk_score = random.randint(0, 39)
            priority = "LOW"
            fraud_prob = round(risk_score / 100.0, 4)
            status = "CLOSED"

        tx_id = f"TXN-{random.randint(100000, 999999)}"
        cust_id = random.choice(customers)
        merch_id = random.choice(merchants)
        amount = round(random.uniform(5.0, 5000.0), 2)
        category = random.choice(categories)
        country = random.choice(countries)
        pm = random.choice(payment_methods)
        device = f"DEV-{random.randint(10000, 99999)}"
        device_type = random.choice(device_types)
        ip = f"192.168.1.{random.randint(2, 254)}"
        
        # Distribute timestamps across past 7 days to exercise trends charts
        days_offset = random.randint(0, 6)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        created_time = datetime.now(timezone.utc) - timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        completed_time = created_time + timedelta(seconds=random.randint(5, 300)) if status in ["COMPLETED", "RESOLVED", "CLOSED"] else None

        metadata = {
            "customer_id": cust_id,
            "merchant": merch_id,
            "amount": amount,
            "currency": "USD",
            "category": category,
            "location_country": country,
            "payment_instrument": pm,
            "device_id": device,
            "device_type": device_type,
            "ip_address": ip,
            "user_age": random.randint(18, 75),
            "account_balance": round(random.uniform(50.0, 15000.0), 2),
            "executive_summary": f"Automated retail fraud investigation for transaction {tx_id}. Risk score: {risk_score}."
        }

        inv = Investigation(
            transaction_id=tx_id,
            status=status,
            priority=priority,
            fraud_probability=fraud_prob,
            risk_score=risk_score,
            overall_confidence=round(random.uniform(0.7, 0.99), 2),
            prediction="Fraud" if risk_score >= 60 else "Legitimate",
            summary=metadata["executive_summary"],
            started_at=created_time,
            completed_at=completed_time,
            created_at=created_time,
            additional_metadata=metadata
        )
        db.add(inv)
        investigation_objects.append((inv, risk_score, priority, created_time, completed_time))

    # Flush to create database primary keys
    await db.flush()

    # ==========================================================
    # 7. Seed detailed Graph results for 10 target investigations
    # ==========================================================
    print("Generating Agent Results, Evidence, Recommendations & Timelines for 10 dossiers...")
    
    for idx in range(10):
        inv, risk_score, priority, created_time, completed_time = investigation_objects[idx]
        inv_id = inv.id

        # Timeline Audit Trail Events
        events = [
            ("TRANSACTION_INGESTED", "Transaction ingested successfully. Initializing analysis pipeline.", None),
            ("FRAUD_PREDICTION_COMPLETED", f"ML Engine completed inference. Risk Score: {risk_score}%.", "FraudPrediction"),
            ("CUSTOMER_AUDIT_COMPLETED", "CustomerInvestigationAgent completed check. Customer profile verified.", "CustomerInvestigationAgent"),
            ("DEVICE_AUDIT_COMPLETED", "DeviceInvestigationAgent verified hardware fingerprints and geographical consistency.", "DeviceInvestigationAgent"),
            ("NETWORK_AUDIT_COMPLETED", "NetworkRiskAgent completed link analysis. Relational attributes mapped.", "NetworkRiskAgent"),
            ("MERCHANT_AUDIT_COMPLETED", "MerchantInvestigationAgent verified chargeback records and processing history.", "MerchantInvestigationAgent"),
            ("KNOWLEDGE_RETRIEVAL_COMPLETED", "KnowledgeAgent retrieved compliance SOPs and playbook rules.", "KnowledgeAgent"),
            ("REASONING_COMPLETED", "ReasoningAgent compiled final consolidated assessment report.", "ReasoningAgent")
        ]

        for ev_idx, (ev_type, ev_desc, agent_name) in enumerate(events):
            evt_time = created_time + timedelta(seconds=ev_idx * 5)
            evt = TimelineEvent(
                investigation_id=inv_id,
                event_type=ev_type,
                title=ev_type.replace("_", " ").title(),
                event_description=ev_desc,
                agent_name=agent_name,
                status="SUCCESS",
                started_at=evt_time,
                completed_at=evt_time + timedelta(seconds=2),
                duration_ms=2000,
                timestamp=evt_time,
                created_at=evt_time,
                additional_metadata={}
            )
            db.add(evt)

        # Agent execution results config mapping
        agent_configs = [
            ("CustomerInvestigationAgent", 0.85, 120, "Customer profile analysis verified.", [
                ("CUSTOMER_VELOCITY", "MEDIUM" if risk_score < 70 else "HIGH", "Customer transaction velocity exceeds average standard baseline.")
            ]),
            ("DeviceInvestigationAgent", 0.90, 80, "Device mapping assessment completed.", [
                ("DEVICE_GEO_MISMATCH", "LOW" if risk_score < 70 else "HIGH", "IP geocoding country coordinates deviate from cardholder billing profile.")
            ]),
            ("NetworkRiskAgent", 0.95, 210, "Relational network graph check completed.", [
                ("SHARED_ATTRIBUTES", "LOW" if risk_score < 80 else "CRITICAL", "Transaction device fingerprint is associated with multiple distinct customer credentials.")
            ]),
            ("MerchantInvestigationAgent", 0.88, 90, "Merchant category check completed.", [
                ("MERCHANT_VELOCITY", "LOW" if risk_score < 50 else "HIGH", "Target merchant is experiencing high refund ratios and velocity spikes.")
            ]),
            ("KnowledgeAgent", 0.92, 340, "Compliance playbooks matches found.", [
                ("PLAYBOOK_MATCH", "MEDIUM" if risk_score < 65 else "HIGH", "Matching rule from Fraud Playbook Section 4.2: High volume checkout pattern.")
            ])
        ]

        for agent_name, conf, latency, summary, ev_list in agent_configs:
            ar = AgentResult(
                investigation_id=inv_id,
                agent_name=agent_name,
                status="SUCCESS",
                confidence_score=conf,
                execution_time_ms=latency,
                summary=summary,
                additional_metadata={"findings": [summary]}
            )
            db.add(ar)
            await db.flush()

            for ev_type, severity, ev_desc in ev_list:
                ev = Evidence(
                    investigation_id=inv_id,
                    agent_result_id=ar.id,
                    type=ev_type,
                    severity=severity,
                    confidence=conf,
                    title=ev_type.replace("_", " ").title(),
                    description=ev_desc,
                    source=agent_name,
                    additional_metadata={}
                )
                db.add(ev)

        # Recommendations list
        recs = [
            ("Freeze Cardholder Credentials", "Temporarily lock account login capabilities and notify cardholder.", "HIGH", "ReasoningAgent"),
            ("Initiate Customer Outcall Verification", "Contact consumer directly to confirm purchase authorization status.", "MEDIUM", "ReasoningAgent"),
            ("Flag Merchant Profile", "Place merchant credential under close velocity monitoring restrictions.", "MEDIUM", "ReasoningAgent")
        ]

        for title, desc, priority_rec, agent in recs:
            rec = Recommendation(
                investigation_id=inv_id,
                title=title,
                description=desc,
                priority=priority_rec,
                generated_by=agent,
                status="PENDING"
            )
            db.add(rec)

    # Commit all changes to the database
    await db.commit()
    print("Database seeding completed successfully.")


async def seed_data(
    admin_email: str,
    admin_password: str,
    analyst_email: str,
    analyst_password: str,
    reset: bool = False,
    db: AsyncSession | None = None,
) -> None:
    """Public wrapper exposing seed_data function with optional database session injector."""
    if db is None:
        async with AsyncSessionLocal() as session:
            await _seed_exec(
                db=session,
                admin_email=admin_email,
                admin_password=admin_password,
                analyst_email=analyst_email,
                analyst_password=analyst_password,
                reset=reset,
            )
    else:
        await _seed_exec(
            db=db,
            admin_email=admin_email,
            admin_password=admin_password,
            analyst_email=analyst_email,
            analyst_password=analyst_password,
            reset=reset,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Reusable database seeder command for roles, permissions, and default accounts."
    )
    parser.add_argument(
        "--admin-email",
        type=str,
        default="admin@investigation.com",
        help="Custom email for the Admin user",
    )
    parser.add_argument(
        "--admin-password",
        type=str,
        default="Admin.123",
        help="Custom password for the Admin user",
    )
    parser.add_argument(
        "--analyst-email",
        type=str,
        default="analyst@investigation.com",
        help="Custom email for the Fraud Analyst user",
    )
    parser.add_argument(
        "--analyst-password",
        type=str,
        default="Analyst.123",
        help="Custom password for the Fraud Analyst user",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="If set, clears existing database tables first",
    )

    args = parser.parse_args()

    asyncio.run(
        seed_data(
            admin_email=args.admin_email,
            admin_password=args.admin_password,
            analyst_email=args.analyst_email,
            analyst_password=args.analyst_password,
            reset=args.reset,
        )
    )


if __name__ == "__main__":
    main()
