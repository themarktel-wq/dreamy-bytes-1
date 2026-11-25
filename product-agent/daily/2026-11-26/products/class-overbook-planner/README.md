# Class Overbook Planner

A single-file tool that shows how many bookings to accept for a class, using your own no-show rate. For each overbooking level it calculates the chance that more people arrive than you have spots, the expected number of people turned away, the expected empty spots and a simple expected net, so you choose the level with numbers instead of gut feeling.

## What you get
- Inputs: capacity, bookings you accept, no-show rate (your own records), revenue per attendee, cost if someone is turned away, number of overbooking levels to compare
- For your chosen bookings: chance of being over capacity, expected turned away, expected empty spots, expected attendees, expected net
- A bar chart of the chance of each attendance number (over-capacity bars in red)
- Comparison table of overbooking levels with your row highlighted and the best net row marked
- Editable, printable booking policy text
- Saves in your browser, works offline, phone friendly

## How it works, and its limits
Each booked person is assumed to show up or not independently, with the same chance (a binomial model). Real classes can differ: friends booking together, weather, class type or time slot all change no-shows, so check the result against your own attendance over time. The "net" figure only counts revenue from attendees and the cost you enter for turning someone away; it ignores goodwill, waitlists and retention. It is a decision aid, not a guarantee. The starting numbers are examples; use your own.

## Who it is for
Yoga, pilates, dance and boutique fitness studio owners and instructors who see no-shows leave empty spots.

Price: Rs 7,000 (about USD 25), one-time. PKR is an approximate conversion at about Rs 280 per USD.
