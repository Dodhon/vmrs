PART,MANUFACTURER,DESCRIPTION are the only correct fields from David's csv
- must match from matching_context.md

copy paste cleaned version of matching_context.md into gemini memory

strict input and output for gemini
- use planning mode to iterate on the plan and rigorously critique plan
- plan before execution!
    - think about if execution is even correct / necessary


ReAct: reason -> Act:
- allows debugging of llm reasoning




copilot studio:
- copilot studio mcp github
- background of how to use mcp in copilot studio



break down written summary and matching into tasks for sprint planning:
1. clean md file
2. etc 
3. etc

do after meeting ^^
- point is to have agile methodology
- helps deliver what client actually wants over time




review db design
- necessary for multiple data sources beyond the manual
- stay focused on what properties/data is guaranteed to be true
- 

different relationships examples
- this vendor only sells these system parts
    - vendor A manufactures only syste codes 1,2, and 3
- this assembly codes only related to these some system etc
    - assembly code xyz is under system code abc
    - same for component
- above are only examples, must generate relationships from manual



meeting with stakeholder
1. start with what we have, and what we think we are missing
2. have stakeholder to tell us what we need
- process or data issue
- we can't control data issue, but we can do process correct
3. ask for contact of the 2 people he mentioned
- ask them for methodology for actually correctly matching
- might need 
4. create vmrs codes of all parts based on llm 



do acceptance testing:
- use llm to make unit testing based of the source of truth excel file that David gave us
- 1st step is to make sure the code actually does what it needs to
    - makes sure the code is actually correct
- review what the stakeholder might actually check



