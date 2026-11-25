# Brief: Booking Guard (d20261125-02)
- Niche: auto detailing. Type: n8n (software). Price USD 45 / PKR 12,600 (1 USD = 280 PKR).
- Unique concept: n8n flow for MOBILE jobs: deposit link, 48h/24h reminders that ask the customer to confirm water, power, keys and parking, weather reschedule that moves the deposit, repeat no-show flag. Built on tools the detailer already owns (Sheets, Twilio/email) instead of $25-129+/mo detailing software (evidence D2) and based on real shop policy patterns (D5, Med).
- Persona: solo mobile detailer. Pain: wasted trips, no water/power access, locked vehicle.
- Build: tools/n8n/d20261125 (build.py, gen_tests.py, sim.js, a copy of the d20261124 simulator); 4 workflows, 25 simulated scenarios.
- Deviations from plan: 4 separate workflows instead of one; the "repeat no-show" flag is a non-refundable-deposit note inside the deposit message (threshold configurable, default 2); deposit payment is not auto-detected.
- No no-show reduction claim is made (no data).
