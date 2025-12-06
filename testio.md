# 📥 **Sample Input 1 (MSG-001)**

```json
{
  "message_id": "MSG-001",
  "source": "email",
  "sender": {
    "name": "Sarah Chen",
    "role": "Product Manager"
  },
  "content": "The customer demo went great! They loved it but asked if we could add real-time notifications and a dashboard export feature. They're willing to pay 20% more and need it in the same timeline. Can we make this work?",
  "project": "PRJ-ALPHA"
}
```

---

# 📤 **Sample Output (MSG-001)**

```
==========================================================================
NION ORCHESTRATION MAP
==========================================================================
Message: MSG-001
From: Sarah Chen (Product Manager)
Project: PRJ-ALPHA

==========================================================================
L1 PLAN
==========================================================================
[TASK-001] → L2:TRACKING_EXECUTION
Purpose: Extract action items from customer request

[TASK-002] → L2:TRACKING_EXECUTION
Purpose: Extract risks from scope change request

[TASK-003] → L2:TRACKING_EXECUTION
Purpose: Extract decision needed

[TASK-004] → L3:knowledge_retrieval (Cross-Cutting)
Purpose: Retrieve project context and timeline

[TASK-005] → L2:COMMUNICATION_COLLABORATION
Purpose: Formulate gap-aware response
Depends On: TASK-001, TASK-002, TASK-003, TASK-004

[TASK-006] → L3:evaluation (Cross-Cutting)
Purpose: Evaluate response before sending
Depends On: TASK-005

[TASK-007] → L2:COMMUNICATION_COLLABORATION
Purpose: Send response to sender
Depends On: TASK-006

==========================================================================
L2/L3 EXECUTION
==========================================================================

[TASK-001] L2:TRACKING_EXECUTION
└─▶ [TASK-001-A] L3:action_item_extraction
Status: COMPLETED
Output:
• AI-001: "Evaluate real-time notifications feature"
  Owner: ? | Due: ? | Flags: [MISSING_OWNER, MISSING_DUE_DATE]
• AI-002: "Evaluate dashboard export feature"
  Owner: ? | Due: ? | Flags: [MISSING_OWNER, MISSING_DUE_DATE]

[TASK-002] L2:TRACKING_EXECUTION
└─▶ [TASK-002-A] L3:risk_extraction
Status: COMPLETED
Output:
• RISK-001: "Adding 2 features with same timeline"
  Likelihood: HIGH | Impact: HIGH
• RISK-002: "Scope creep for 20% revenue increase"
  Likelihood: MEDIUM | Impact: MEDIUM

[TASK-003] L2:TRACKING_EXECUTION
└─▶ [TASK-003-A] L3:decision_extraction
Status: COMPLETED
Output:
• DEC-001: "Accept or reject customer feature request"
  Decision Maker: ? | Status: PENDING

[TASK-004] L3:knowledge_retrieval (Cross-Cutting)
Status: COMPLETED
Output:
• Project: PRJ-ALPHA
• Current Release Date: Dec 15
• Days Remaining: 20
• Code Freeze: Dec 10
• Current Progress: 70%
• Team Capacity: 85% utilized
• Engineering Manager: Alex Kim
• Tech Lead: David Park

[TASK-005] L2:COMMUNICATION_COLLABORATION
└─▶ [TASK-005-A] L3:qna
Status: COMPLETED
Output:
• Response: "Great news on the demo! For the feature request:

WHAT I KNOW:
• Current timeline: Dec 15 (code freeze Dec 10)
• Team capacity: 85% utilized
• Progress: 70% complete

WHAT I'VE LOGGED:
• 2 action items for feature evaluation
• 2 risks flagged (timeline + scope creep)
• 1 pending decision

WHAT I NEED:
• Complexity estimates from Engineering (Alex Kim / David Park)
• Go/no-go decision from leadership

I cannot assess feasibility without Engineering input on whether 2 new features can fit in 20 days at 85% capacity."

[TASK-006] L3:evaluation (Cross-Cutting)
Status: COMPLETED
Output:
• Relevance: PASS
• Accuracy: PASS
• Tone: PASS
• Gaps Acknowledged: PASS
• Result: APPROVED

[TASK-007] L2:COMMUNICATION_COLLABORATION
└─▶ [TASK-007-A] L3:message_delivery
Status: COMPLETED
Output:
• Channel: email
• Recipient: Sarah Chen
• CC: Alex Kim (Engineering Manager)
• Delivery Status: SENT

==========================================================================
```

---

# 🧪 **Test Case Inputs (MSG-101 → MSG-106)**

## **MSG-101 — Simple Status Question**

```json
{
  "message_id": "MSG-101",
  "source": "slack",
  "sender": { "name": "John Doe", "role": "Engineering Manager" },
  "content": "What's the status of the authentication feature?",
  "project": "PRJ-BETA"
}
```

---

## **MSG-102 — Feasibility Question**

```json
{
  "message_id": "MSG-102",
  "source": "email",
  "sender": { "name": "Sarah Chen", "role": "Product Manager" },
  "content": "Can we add SSO integration before the December release?",
  "project": "PRJ-ALPHA"
}
```

---

## **MSG-103 — Decision/Recommendation Request**

```json
{
  "message_id": "MSG-103",
  "source": "email",
  "sender": { "name": "Mike Johnson", "role": "VP Engineering" },
  "content": "Should we prioritize security fixes or the new dashboard?",
  "project": "PRJ-GAMMA"
}
```

````
---

## **MSG-104 — Meeting Transcript**
```json
{
  "message_id": "MSG-104",
  "source": "meeting",
  "sender": { "name": "System", "role": "Meeting Bot" },
  "content": "Dev: I'm blocked on API integration, staging is down. QA: Found 3 critical bugs in payment flow. Designer: Mobile mockups ready by Thursday. Tech Lead: We might need to refactor the auth module.",
  "project": "PRJ-ALPHA"
}
````

---

## **MSG-105 — Urgent Escalation**

```json
{
  "message_id": "MSG-105",
  "source": "email",
  "sender": { "name": "Lisa Wong", "role": "Customer Success Manager" },
  "content": "The client is asking why feature X promised for Q3 is still not delivered. They're threatening to escalate to legal. What happened?",
  "project": "PRJ-DELTA"
}
```

---

## **MSG-106 — Ambiguous Request**

```json
{
  "message_id": "MSG-106",
  "source": "slack",
  "sender": { "name": "Random User", "role": "Unknown" },
  "content": "We need to speed things up",
  "project": null
}
```

---

# ✔ End of File
