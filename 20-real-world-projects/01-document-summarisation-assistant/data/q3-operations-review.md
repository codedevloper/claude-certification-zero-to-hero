# Northwind Lending: Q3 FY2026 Operations Review

Synthetic document for training purposes. Northwind Lending is a fictional company and every figure below is invented.

## 1. Purpose and scope

This review covers the loan servicing, customer operations, technology and risk functions of Northwind Lending for the third quarter of fiscal year 2026 (July to September). It was prepared by the Operations Excellence Office for the executive committee, the engineering leadership group and the compliance team. Each section ends with the decisions taken and the open items carried into Q4.

## 2. Loan servicing performance

Loan servicing processed 184,200 payments in Q3, up 6.4% on Q2. The straight-through processing rate reached 91.3%, against a target of 93%. The shortfall came mainly from manual exceptions on payments made by bank transfer without a valid reference number, which accounted for 5,870 exceptions during the quarter.

Average time to resolve a payment exception fell from 3.1 business days to 2.2 business days after the exception queue was re-sorted by age rather than by amount. The servicing team believes a further reduction is possible if the reference-number validation is moved to the customer portal before submission.

Early-stage delinquency (accounts 1 to 29 days past due) rose to 2.8% of the active book, compared with 2.5% at the end of Q2. Late-stage delinquency (60 or more days past due) remained flat at 0.9%. The collections team attributes the early-stage increase to a cluster of accounts whose payment date moved when the payroll provider of one large employer changed its pay cycle.

Decision: the servicing director approved a pilot of proactive payment-date change offers for affected customers, starting in October.

## 3. Customer operations

The contact centre handled 96,400 contacts in Q3, of which 58% were phone calls, 31% were secure messages and 11% were web chat. Average speed of answer for phone calls was 74 seconds, which breaches the internal service level of 60 seconds. The breach was concentrated in the first two weeks of September, when a fee-statement mailing generated a spike of 12,300 extra calls.

First-contact resolution improved to 78% from 75% in Q2. Customer satisfaction measured by post-contact survey was 4.3 out of 5, unchanged from the previous quarter. Complaints logged under the formal complaints procedure fell to 412 from 455.

The knowledge base used by agents now contains 640 articles. An audit found that 47 articles referenced the old fee schedule. All 47 were corrected by 19 September.

Action: the customer operations lead will review mailing schedules with the marketing team so that large mailings are staggered over at least two weeks. Due date: 15 November.

## 4. Technology and platform

The loan servicing platform achieved 99.95% availability against a target of 99.9%. There was one Severity 2 incident on 22 August, when a certificate expired on the integration with the payment gateway. Card payments failed for 38 minutes and 1,140 customers saw an error message. The certificate was renewed manually and no payments were lost because failed attempts were retried automatically.

The post-incident review found that certificate expiry dates were tracked in a spreadsheet rather than in the monitoring system. Engineering has since added expiry alerts at 30, 14 and 3 days for all 112 externally facing certificates.

The migration of the document management system to the new cloud tenancy is 70% complete. Remaining work covers archived correspondence older than seven years, which must first be reviewed against the records retention schedule. The migration is forecast to finish in December, one month later than planned, because the retention review took longer than estimated.

Cloud infrastructure spend was 1.42 million dollars in Q3, 8% above budget. The overspend is explained by duplicate storage during the document migration, which will end when the old tenancy is decommissioned.

Decision: the engineering leadership group approved decommissioning the old tenancy within 30 days of migration sign-off.

## 5. Risk, compliance and controls

Internal audit completed its review of access management for the servicing platform. It raised two medium-rated findings. First, 23 user accounts belonging to staff who had changed roles still held privileges from their previous team. Second, quarterly access recertification for privileged accounts was completed 11 days late. Both findings have agreed remediation plans with a due date of 31 December.

The compliance team completed the annual review of collections call scripts. Three scripts were updated to make the hardship-support options clearer. No regulatory breaches were identified in the quarter.

A third-party risk assessment of the new mailing vendor was completed before contract signature. The vendor was rated medium risk because it subcontracts printing to a second company. A contract clause now requires notification before any change of subcontractor.

Risk: if early-stage delinquency continues to rise at the Q3 rate, the credit risk team estimates that the impairment provision would need to increase by about 0.6 million dollars in Q4.

## 6. People

Operations headcount was 412 full-time equivalents at the end of the quarter, against a plan of 420. Voluntary attrition in the contact centre was 4.1% for the quarter. Twenty-six new agents completed induction training, and the induction programme was shortened from six weeks to five weeks after a review of shadowing time.

## 7. Open items carried into Q4

1. Pilot of proactive payment-date change offers (owner: servicing director, starts October).
2. Staggered mailing schedule agreed with marketing (owner: customer operations lead, due 15 November).
3. Completion of the document management migration (owner: head of platform engineering, forecast December).
4. Remediation of the two access management audit findings (owner: identity and access manager, due 31 December).
5. Move payment reference validation into the customer portal (owner: digital product manager, business case due in Q4).
