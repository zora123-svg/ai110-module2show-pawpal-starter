# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Three core actions user is able to perform is to enter their infomation and pet information. The next one is that a user should be able to add/edit/delete tasks. And finally their should be a way to generate a daily schedule based off what the user enters. To go into more detail their should be a way to take in user's information like name, age, date of birth, and ect. But there also should be a way to take in the pet infomation like name, type of pet (dog,cat,ect...). Also you can include species if applicable. Then we move on to tasks. So a user should be able to create, update, and delete a task. To go deeper into this there could be a hierachy within task if user specifies it. Meaning some tasks are more important than others and somehow duration is going to fit within the tasks. Finally the daily schedule should have some contrainsts on it I'm not sure what constraints to add right now but I do know there should be a contraint.

Class: Owner - Take in owner info, display it, update it.
Class: Pets - Take in pet info, display it, update it.
Class: Tasks - Basic crud operators and there should be a way for a user to specify the duration and day the task is on.
Class: DailySchedule - It will take a task or tasks to generate a schedlue based on the user input. There should also be a way that a user can check of tasks within that daily schedule.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
