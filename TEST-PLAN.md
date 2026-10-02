# Test plan

What needs testing before we can honestly say where this system works and where
it does not.

The point of all of it is to answer three questions at the end:

1. Does it let the right people in, and how often does it fail to?
2. Does it keep the wrong people out, and which attacks does it miss?
3. What conditions does it need in order to work properly?

Results go in the build log. This file is just the checklist.

---

## How to run any test

These rules came out of getting things wrong earlier, so they are worth keeping.

- Two runs of everything before believing a number. If the two runs disagree,
  that disagreement is the result.
- Ten seconds per run, which gives roughly 30 to 60 frames.
- Change one thing at a time. If lighting and distance both move, the result
  means nothing.
- Mark the standing spot on the floor with tape and use it every time.
- Watch the face width on screen. Aim for 200 to 250 pixels, unless distance is
  the thing being tested.
- Record all three models, not just the one that looks best.
- Note which camera was used. The camera has changed results more than the model
  choice did.
- Never write numbers down by eye. Always record to the file.

---

## Part A. Recognition. Does it know who someone is?

### A1. The basics

- [ ] Each enrolled person against their own reference, good light, facing the
      camera. This is the baseline everything else gets compared to.
- [ ] Each enrolled person against everyone else's reference, to find out
      whether it ever confuses two people.
- [ ] Someone not enrolled at all. Should match nobody.

### A2. Does it still recognise you when you look different?

- [ ] Glasses on and off
- [ ] Sunglasses
- [ ] Cap, or hood up
- [ ] Hard hat, once we have one
- [ ] Hard hat plus safety glasses, which is the real case at a gate
- [ ] Face mask
- [ ] Beard growth over the weeks of the project
- [ ] Hair tied up versus down
- [ ] High collar or scarf

### A3. Angle and position

- [ ] Facing the camera, then 15, 30, 45, 60 and 90 degrees
- [ ] Looking down, as if at the ground
- [ ] Looking up
- [ ] Head tilted sideways
- [ ] Walking past rather than standing still

### A4. How many people can it tell apart?

- [ ] 5 people enrolled
- [ ] 10
- [ ] 20, or as many as we can get

More people means more chances of a mix-up, and we need to know whether the
scores start crowding together as the list grows.

### A5. The threshold

- [ ] Collect enough data to draw the curve: for every possible cut-off, how
      many people get wrongly refused and how many get wrongly accepted
- [ ] Pick a number and be able to defend it

---

## Part B. Liveness. Is it a real person?

### B1. Attacks with a screen

- [ ] Phone screen, full brightness
- [ ] Phone screen, dimmed
- [ ] Phone screen, tilted to cut the glare
- [ ] Tablet or laptop screen, which is bigger and may behave differently
- [ ] Video of a face playing, rather than a still photo
- [ ] Each of the above at close, normal and far distance

### B2. Attacks with paper

- [ ] Printed photo with the border left on
- [ ] Printed photo cut out to the edge of the face
- [ ] Glossy photo paper versus ordinary office paper
- [ ] Access card with a photo on it
- [ ] Held in hand versus laid flat on a surface
- [ ] Each at a controlled distance, so the model gets the same crop every time

### B3. Harder attacks, if time allows

- [ ] Paper mask with eye holes, held in front of the face
- [ ] Paper mask worn
- [ ] Photo held behind glass or clear plastic
- [ ] Printed photo slightly curved rather than flat

### B4. Does it wrongly reject real people?

- [ ] Each person in good light, as the baseline
- [ ] The same in every lighting condition from Part D
- [ ] With glasses, cap, hood, hard hat
- [ ] At different distances
- [ ] While moving rather than standing still

---

## Part C. The two parts together

Once recognition and liveness are joined up, the combination needs testing on
its own. A system can pass both halves separately and still behave badly.

- [ ] Right person, real face. Should open.
- [ ] Right person, photo of them. Should refuse.
- [ ] Wrong person, real face. Should refuse.
- [ ] Wrong person, photo of them. Should refuse.
- [ ] Nobody in front of the camera. Should do nothing.
- [ ] Two people in frame at once. What does it decide, and whose face does it
      use?
- [ ] Someone walking past behind the person at the gate. Does it get confused?
- [ ] Person is accepted, walks away, comes back. Same result each time?

---

## Part D. Conditions it has to cope with

### D1. Lighting

- [ ] Bright, indoors
- [ ] Normal room light
- [ ] Dim
- [ ] Dark, only a screen glowing
- [ ] Backlit, bright window behind the person
- [ ] Backlit with a lamp in front of the face, to see whether that fixes it
- [ ] Harsh light from one side, half the face in shadow
- [ ] Outdoors in daylight
- [ ] Outdoors at dusk

### D2. Distance and position

- [ ] 0.5, 1, 1.5, 2 and 3 metres, marked on the floor
- [ ] The distance where detection stops working completely
- [ ] Camera too low, at eye level, and too high
- [ ] Person off to one side rather than straight in front

### D3. The camera itself

This has turned out to matter more than anything else, so it gets its own
section.

- [ ] USB camera versus phone stream, same conditions, to measure the difference
- [ ] Autofocus on and off
- [ ] Manual exposure versus automatic, especially in backlight
- [ ] Different resolutions, since lower resolution means fewer pixels on the
      face
- [ ] The Axis camera, once SSG provide it
- [ ] Infrared mode, if the Axis camera has one

### D4. Weather, when we can

- [ ] Water sprayed on the housing, to simulate rain
- [ ] Fog or condensation on the lens
- [ ] Snow, if the weather provides it

---

## Part E. Does it work well enough to actually use?

- [ ] How long one decision takes, start to finish
- [ ] The same on the Jetson rather than the laptop
- [ ] Whether it slows down after running for an hour, since the Jetson is
      fanless and gets hot
- [ ] Memory use, since the Jetson only has 4 GB
- [ ] What happens when the same person tries twice in a row
- [ ] What happens when someone is refused. Is the reason clear to them?

---

## What we are not testing, and why

Worth writing down so nobody assumes it was covered.

- Silicone or 3D printed masks. Too expensive, and far beyond what anyone would
  realistically do at a factory gate.
- Deepfake video. Out of scope for a ten week project.
- Twins or very similar siblings. We have no access to any.
- Hundreds or thousands of enrolled people. We can enrol twenty at most.
- Ageing over years. The project is ten weeks.
- Tailgating, meaning someone walking in behind a valid entry. Not solvable in
  software without a turnstile, so it goes in the limitations instead.

---

## Order to do things in

If time runs short, this order produces the most useful results.

1. Attacks with paper, Part B2. This is the known weakness and it needs proper
   numbers.
2. Lighting, Part D1. The conditions a real gate actually faces.
3. Real people being wrongly refused, Parts B4 and A1. If it refuses legitimate
   workers it does not matter how secure it is.
4. More people enrolled, Part A4. Everything so far is three people.
5. The two parts joined together, Part C.
6. Screen attacks, Part B1. Already looks strong, so lower priority.
7. Speed and the Jetson, Part E.
8. Everything else.
