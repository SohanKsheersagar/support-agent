# Trailhaven Company Knowledge Pack

*Doc 2 of 3. This is the content the agent answers from. Split each article below into its own file (for example `kb/returns-policy.md`) and index them with the `source_id` shown in brackets. Everything here is fictional.*

## Part A. Company profile

**Trailhaven Outfitters** sells outdoor gear online: tents, sleeping bags, backpacks, hiking boots, apparel, and accessories. Founded 2017, based in Denver, Colorado. Ships to the US and Canada. Roughly 1,200 support tickets per week.

- **Support hours:** Monday to Friday, 8am to 8pm Mountain Time; Saturday 9am to 5pm. Closed Sunday and major US holidays.
- **Support email:** help@trailhaven.example
- **Brand promise:** "Gear you can trust, people who've used it."
- **Customer tiers:** Standard, Summit (spent over $1,000 in 12 months), and VIP (flagged manually; always escalated to a human).
- **Carriers:** UPS Ground and USPS Priority. Canada orders ship via UPS Standard.

### Product categories and SKU prefixes

| Prefix | Category | Examples |
| --- | --- | --- |
| TNT | Tents | TNT-2P-ALP (2-person alpine tent) |
| SLP | Sleeping bags and pads | SLP-20F-DWN (20F down bag) |
| BAG | Backpacks | BAG-45L-TRK (45L trekking pack) |
| BTS | Boots and footwear | BTS-MID-WP (mid waterproof boot) |
| APP | Apparel | APP-JKT-SHL (shell jacket) |
| ACC | Accessories | ACC-STV-LGT (lightweight stove) |

## Part B. Tone and voice guide \[KB-TONE-001\]

**Who we sound like:** a friendly, experienced outdoors person who respects the customer's time.

**Do:**

- Open with the customer's first name and one short empathetic line when something went wrong.
- Answer the question in the first two sentences, then add detail.
- Use plain words, short paragraphs, and a clear next step.
- Cite specifics: order number, dates, amounts, tracking numbers.
- Close with "Happy trails," and the agent name ("Trailhaven Support" for drafts).

**Don't:**

- Over-apologize. One apology maximum per reply.
- Make promises outside policy (never write "I guarantee", "definitely", "100%").
- Mention internal tools, policies by rule id, or that the reply was AI-drafted.
- Give legal, medical, or safety certification advice.
- Use exclamation marks more than once.

**Length:** 80 to 160 words for simple tickets, up to 250 for complex ones.

**Example (good):**

> Hi Jordan, sorry your pack arrived with a torn strap. Since it was delivered 6 days ago, you're well within our 30-day window. I've started a replacement for order TH-10482 and you'll get a prepaid return label by email shortly. Once the label arrives, drop the damaged pack at any UPS location; your replacement ships when the carrier scans it. Happy trails, Trailhaven Support

## Part C. Policies

### Returns policy \[KB-RET-001\]

- **Window:** 30 days from the delivery date for unused items in original condition with tags.
- **Summit tier:** 45 days.
- **Free return shipping** if the item is defective, damaged, or we sent the wrong item. Otherwise a $7.95 return label fee is deducted from the refund.
- **Non-returnable:** worn footwear, used sleeping bags and pads (hygiene), gift cards, items marked Final Sale, custom-printed items.
- **Refund method:** original payment method, 5 to 7 business days after we receive and inspect the item.
- **Exchanges:** same item in a different size or color, subject to stock. Different item = return plus new order.
- Items returned after the window are not eligible for refund; store credit may be offered only by a human agent.

### Refund approval and authority \[KB-REF-001\] (internal)

This is the policy the refund gate in code enforces.

| Refund amount | Condition | Who can approve |
| --- | --- | --- |
| Up to $50.00 | Within return window, reason matches policy | May be pre-approved by the agent system, still shown to a human reviewer in MVP |
| $50.01 to $200.00 | Within return window | Tier-1 support agent must approve |
| Over $200.00 | Any | Team Lead must approve |
| Any amount | Outside the window, partial refund, goodwill, or an exception | Team Lead must approve |
| Any amount | Customer flagged VIP or fraud-risk | Always escalate, no auto handling |

The agent may never promise a refund in writing before approval. Draft language must say "I've submitted your refund request" or "our team will review", not "you will be refunded", unless the proposal is already approved.

### Shipping policy \[KB-SHIP-001\]

| Method | Cost (US) | Delivery estimate |
| --- | --- | --- |
| Standard (UPS Ground) | $6.95, free over $75 | 3 to 7 business days |
| Expedited (USPS Priority) | $14.95 | 2 to 3 business days |
| Overnight | $29.95 | 1 business day, order by 1pm MT |
| Canada (UPS Standard) | $16.95 | 6 to 10 business days, duties paid by customer |

- Orders ship within 1 business day (2 during sale events).
- Tracking email is sent when the label is created; tracking updates may lag up to 24 hours.
- We do not ship to PO boxes (except via USPS Priority) or outside the US and Canada.

### Lost, delayed, and damaged packages \[KB-SHIP-002\]

- **Delayed:** if tracking shows no movement for 3 business days, we open a carrier inquiry. Tell the customer to expect an update within 2 business days.
- **Lost:** if a package is 10 business days past the latest delivery estimate, or the carrier marks it lost, we reship at no cost or refund in full. Needs Tier-1 approval if over $50.
- **Marked delivered but not received:** ask the customer to check with neighbors and household members and wait 24 hours, then open a carrier trace. Reship or refund after trace result. Escalate if the customer has had 2 or more such claims in 12 months.
- **Damaged on arrival:** request a photo of the item and the box within 14 days of delivery; then replacement or refund per customer preference.

### Warranty policy \[KB-WAR-001\]

- **Tents, sleeping bags, backpacks:** 2-year warranty against manufacturing defects (seams, zippers, stitching, delamination).
- **Boots:** 1-year warranty against sole separation and waterproofing failure.
- **Apparel:** 1-year warranty against manufacturing defects.
- **Not covered:** normal wear and tear, damage from misuse, UV damage, damage from improper storage, cuts and burns, modifications.
- **Process:** customer sends photos and order number; if the defect is plausible, a human agent approves a replacement or repair. The agent may draft the request for photos but may not confirm coverage.

### Price adjustment and promotions \[KB-PRC-001\]

- Price adjustments within 14 days of purchase if the item goes on sale on trailhaven.example. Handled by a human agent.
- Promo codes cannot be applied after an order is placed.
- Gift cards never expire and cannot be redeemed for cash.

### Order changes and cancellations \[KB-ORD-001\]

- Orders can be edited or cancelled until the status changes to `Processing` (usually within 2 hours of placement).
- After that, the customer must wait for delivery and use the returns process.
- Address changes after shipment are not possible; the package may be redirected via the carrier.

### Privacy and security rules for support \[KB-SEC-001\] (internal)

- Never ask for or repeat full card numbers, CVV, or passwords.
- Verify identity before sharing order details: the ticket's sender email must match the email on the order, or the customer must provide the order number plus the ZIP code on the order.
- Do not share another customer's information under any circumstances.
- If a ticket contains a card number, redact it and tell the customer not to send card details by email.

## Part D. Escalation matrix \[KB-ESC-001\] (internal)

The agent must escalate to a human, with a written summary, in these cases. These are enforced by deterministic rules and a classifier.

| Trigger | Escalate to | Priority |
| --- | --- | --- |
| Injury, fire, or any safety incident involving gear | Team Lead | Urgent |
| Legal threat, mention of lawyer, regulator, or lawsuit | Team Lead | Urgent |
| Chargeback or payment dispute mentioned | Team Lead | High |
| Press, social media influencer, or public review threat | Team Lead | High |
| Suspected fraud or account takeover | Team Lead | Urgent |
| VIP customer | Assigned account manager | High |
| Refund over $200 or any policy exception | Team Lead | High |
| Harassment or abusive language toward staff | Team Lead | Normal |
| Customer has contacted us 3 or more times in 7 days about the same issue | Tier-1 agent | High |
| Agent confidence below 0.70, or KB has no relevant answer | Tier-1 agent | Normal |
| Request involves personal data deletion or privacy rights | Team Lead | High |

## Part E. Knowledge base articles (customer-facing)

Each article below is one KB document. Keep them short so retrieval stays precise.

### How do I track my order? \[KB-FAQ-001\]

You will receive a tracking email once your order ships, usually within 1 business day. Click the tracking link, or log in to your Trailhaven account and open **Orders**. Tracking can take up to 24 hours to show movement after the label is created. If there is no movement for 3 business days, contact us and we will open a carrier inquiry.

### How do I start a return? \[KB-FAQ-002\]

Log in, open **Orders**, choose the item, and select **Start a return**. Guests can use the Returns page with the order number and email. You will get a prepaid label by email if the return is free, or a label with a $7.95 fee deducted from your refund. Pack the item in its original packaging with tags and drop it at the carrier. Refunds are issued 5 to 7 business days after we receive it.

### How do I choose the right sleeping bag temperature rating? \[KB-PRD-001\]

The rating on our sleeping bags is the **lower limit**: the lowest temperature at which an average sleeper stays warm. For comfort, choose a bag rated 10 to 15 degrees Fahrenheit colder than the lowest temperature you expect. Women often sleep colder, so consider the comfort rating. A liner adds roughly 5 to 10 degrees. A sleeping pad with an R-value of 4 or higher is recommended for winter camping.

### How do I size a backpack? \[KB-PRD-002\]

Pack size depends on trip length and torso length, not height. Measure from the bony bump at the base of your neck to the top of your hip bones. Our 45L Trekking Pack comes in S (15 to 17.5 in), M (17.5 to 19.5 in), and L (19.5 to 21.5 in). For weekend trips choose 30 to 50 liters; for 3 to 5 days choose 50 to 70 liters.

### Are your waterproof boots really waterproof? \[KB-PRD-003\]

Our Mid Waterproof Boot uses a waterproof membrane and sealed seams, which keeps water out in rain, wet grass, and shallow streams. It is not designed for submersion above the ankle. To maintain performance, clean boots after muddy trips and re-apply a DWR treatment every 6 months of regular use. Boots are not warranted against waterproofing loss caused by lack of care or leather drying out near heat.

### How do I care for my down sleeping bag? \[KB-CARE-001\]

Store it loosely in the large cotton storage sack, never compressed long term. Spot clean when possible. When washing is needed, use a front-loading machine on gentle with a down-specific cleaner, rinse twice, and dry on low heat with 2 or 3 clean tennis balls until fully dry, which can take 3 or more hours. Do not dry clean, use fabric softener, or use a top-loading machine with an agitator.

### How do I clean and re-waterproof my tent? \[KB-CARE-002\]

Set up the tent, wipe with a sponge and cool water, and let it dry fully before packing. Do not machine wash or use detergent. To restore water repellency, apply a tent-safe spray-on DWR product after the tent is clean and dry. Seam leaks can be fixed with seam sealer, which is sold separately. Store the tent dry and loosely packed, away from direct sunlight.

### What is the status of my warranty claim? \[KB-WAR-002\]

Warranty claims are reviewed within 3 business days of receiving photos and your order number. You will get an email with a decision. If approved, we send a replacement or arrange a repair and cover shipping. If more details are needed, we will ask for them in the same thread.

### Can I change the shipping address on my order? \[KB-ORD-002\]

Yes, if the order has not reached **Processing** status. Reply with the new address as soon as possible. Once an order ships, we cannot change the address; contact the carrier using the tracking number to request a redirect, or wait for delivery and use the returns process.

### Do you offer student, military, or first responder discounts? \[KB-PRC-002\]

Yes. Verified students, active and veteran military, and first responders get 10% off through our verification partner. The discount applies to full-price items only and cannot be combined with other promotions or applied after checkout.

### What payment methods do you accept? \[KB-PAY-001\]

Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, Google Pay, and Trailhaven gift cards. We do not accept checks or cash on delivery. Charges appear as TRAILHAVEN OUTFITTERS on your statement. We never store full card numbers.

### My item is out of stock. When will it be back? \[KB-STK-001\]

Restock dates are estimates and can change. You can sign up for **Notify me** on the product page and we will email you the moment it is back. We cannot reserve out-of-stock items or place backorders.

## Part F. Canned macros for human agents (used as style examples)

- **Request photos for damage:** "Could you send a photo of the item and one of the shipping box? That helps us file the claim quickly."
- **Escalation notice to customer:** "I've passed your case to a senior team member who will follow up by \[time window\]. You won't need to repeat anything."
- **Out-of-scope:** "That's a bit outside what I can confirm, so I've asked a specialist to take a look."

## Part G. Maintenance notes for you (the builder)

- Version every KB article; the agent should cite `source_id` and version in traces.
- When a human edits a draft because a fact was wrong, fix the KB article first, then add an eval case.
- Add 10 to 15 more articles as you discover gaps. A thin KB is the number one reason support agents make things up.
