# Implementation Handbook

The Ultimate Building Block for Equipment & Maintenance Reporting

New Unilated Version!

**Technology & Maintenance Council** 

**A Technical Council of American Trucking Associations** 

**ATA:**BUSINESS SOLUTIONS

# Implementation Handbook

## Version 2.0

Published by

#### Technology & Maintenance Council of American Trucking Associations

950 N. Glebe Road, Suite 210 Arlington, VA 22203

Phone: (703) 838-1763 E-mail: tmc@trucking.org web: http://tmc.trucking.org

Copyright 1998, 1999, 2001. 2003, 2004, 2005, 2007, 2020 Technology & Maintenance Council, American Trucking Associations, Inc.

> All Rights Reserved. No portion of this manual may be reproduced and distributed without permission from the publisher.

> > Robert Braswell, TMC Executive Director Jack Poster, VMRS Services Manager

### Table of Contents

| Welcome to VMRS <sup>TM</sup> !                                      | 1  |
|----------------------------------------------------------------------|----|
| 1. An Introduction to VMRS <sup>™</sup>                              | 2  |
| What is VMRS?                                                        | 2  |
| A Structured Coding System                                           | 2  |
| Recognized Internationally                                           | 3  |
| 15 Distinct Advantages to VMRS                                       | 3  |
| VMRS™ Version 2.0 Licensing                                          | 4  |
| Frequently Asked Questions on VMRS™ Licensing                        | 5  |
| 2. Requirements for Using VMRS <sup>TM</sup>                         | 7  |
| What Are the Basic Requirements for Implementing VMRS?               | 7  |
| The Equipment Master Record                                          | 7  |
| Equipment Vocation Codes: Code Key 1                                 | 7  |
| Reason for Repair Codes: Code Key 14                                 | 8  |
| Work Accomplished Codes: Code Key 15                                 | 9  |
| VMRS System Level Codes: Code Key 31                                 | 9  |
| Assembly Level Codes: Code Key 32                                    |    |
| Component Level Codes: Code Key 33                                   |    |
| Manufacturer/Supplier/Brand Identification: Code Key 34              |    |
| Technician Part Failure Codes: Code Key 18                           |    |
| Summary                                                              |    |
| 3. How to Implement VMRS <sup>TM</sup>                               |    |
| Implementation Preparation                                           | 14 |
| 4. Preparing Effective Vehicle Maintenance Management Reports        | 21 |
| Introduction                                                         |    |
| Equipment Maintenance Cost Reports                                   | 21 |
| Equipment Maintenance Analysis by Vehicle System Codes               | 25 |
| Fleet Maintenance by Equipment System Codes                          | 25 |
| Equipment Maintenance by Reason for Repair                           |    |
| Maintenance Facility Summary Analysis                                | 29 |
| Maintenance Facility Rework Analysis                                 | 29 |
| Warranty Claims Analysis                                             | 29 |
| Parts Usage Analysis                                                 | 29 |
| 5. Integrating Maintenance, Fuel and Oil Information                 |    |
| Data Collection and Processing                                       |    |
| 6. Shop Start-Up Procedures for VMRS                                 |    |
| Initial Planning for VMRS Implementation                             |    |
| Repair Order Forms and Procedures                                    |    |
| Training Personnel to Use the VMRS™ Repair Order Form                |    |
| Shop and Central Office Files                                        | 45 |
| Equipment Master Record Forms                                        |    |
| Procedure Manuals Development                                        | 46 |
| Follow-up Procedures                                                 | 46 |
| 7. How to Prepare VMRS <sup>™</sup> Forms                            |    |
| Instructions for Completing Equipment Master Records                 |    |
| Equipment Master Record — Power Units (Form 1)                       |    |
| Equipment Master Record - Continuation Form (Form 25)                |    |
| Equipment Master Record—Mechanical Refrigeration Units (Form 3)      |    |
| Equipment Master Record—Material Handling Units (Form 4)             | 96 |
| Equipment Master Record—Trailers, Containers and Converters (Form 2) |    |
| Instructions for Completing VMRS <sup>™</sup> Repair Orders          |    |
| Instructions for Completing the VMRS Equipment File - Form 30        |    |
| Instructions for Completing the VMRS Repair Order Log - Form 20/21   |    |

| 7a Samples of VMRS <sup>TM</sup> Forms                                      | 134            |
|-----------------------------------------------------------------------------|----------------|
| Equipment Master Record: Power Units                                        | 13/            |
| Completed Equipment Master Record: Power Units — Form 1                     |                |
| Equipment Master Record: Trailore Converters Containers — Form 2            |                |
| Completed Equipment Master Record: Trailars — Containers — Form 2           |                |
| Equipment Master Record: Mechanical Refrigeration Unite — Form 3            |                |
| Completed Equipment Master Pocord: Politicarter Directory Politics — Form 2 |                |
| Completed Equipment Master Record: Material Handling Units — Form 4         |                |
| Equipment Master Record: Material Handling Units — Form 4                   |                |
| Completed Equipment Master Record: Material Handling Units — Form 4         |                |
| Completed Repair Order—Form 6 (Data Processing Copy)                        |                |
| Completed Repair Order—Form 6 (Technician's Copy)                           |                |
| Sample Special Repair Order—Form 7                                          |                |
| Repair Order Continutation Form—Form 15                                     |                |
| Repair Order Log—Form 20/21                                                 |                |
| Equipment File—Form 30                                                      | 14/            |
| ADDENIDIV                                                                   |                |
| AFFENDIA                                                                    | 1 0/ A 1       |
| Appendix I: The Complete VMKS <sup>114</sup> Coding Convention— Code Keys   | 1 - 84 A-1     |
| List of Obsolete Code Keys                                                  |                |
| Code Key 1: Equipment Vocation                                              |                |
| Code Key 2: Equipment Category                                              |                |
| Code Key 3: Axle Configuration                                              | A-8            |
| Code Key 4: Cab Types (All Vehicles)                                        |                |
| Code Key 5: Power Source                                                    | A-10           |
| Code Key 6: Horsepower (Kilowatt) Range                                     | A-11           |
| Code Key 7: Transmission Types For Power Units                              |                |
| Code Key 8: Forward Transmission Speeds                                     | A-13           |
| Code Key 9: (Obsolete) Reserved for Future Use                              | A- 2           |
| Code Key 10: Body Types for Trailers, Containers, Converters                | A-14           |
| Code Key 11: DOT Motor Carrier Specifications for Tank Vehicles             | A-16           |
| Code Key 12: Trailer Height                                                 | A-17           |
| Code Key 13: Trailer Length                                                 | A-18           |
| Code Key 14: Reason for Repair                                              | A-19           |
| Code Key 15: Work Accomplished                                              | A-23           |
| Code Key 16: Repair Priority                                                | A-25           |
| Code Key 17: Repair Site                                                    | A <b>-2</b> 6  |
| Code Key 18: Technician Part Failure Code                                   | A <b>-</b> 27  |
| Code Key 19: Indirect Labor Activities                                      | A-29           |
| Code Key 20: Equipment Status Code                                          | A-33           |
| Code Key 21: New & Retread Tire Out-of-Service Conditions                   | A-34           |
| Code Key 22: Tire Management Removal Code                                   | A-37           |
| Code Key 23: Tire Position Code                                             | A- 37          |
| Code Key 24: Maintenance Status                                             | A-39           |
| Code Keys 25-30: (Obsolete) Reserved for Future Use                         | A-2            |
| Code Key 31: System Codes                                                   | A-40           |
| Code Key 32: Assembly Codes                                                 | A-85           |
| Code Key 33: Component Codes                                                | A-99           |
| Code Key 34: Manufacturer/Supplier/Brand Codes                              | A-100          |
| Code Key 35: Engine Configuration                                           | A-180          |
| Code Key 36: Power Take Off                                                 | A-180          |
| Code Key 37: Axle Configuration                                             | A <b>-</b> 181 |
| Code Key 38: Axle (Powered) Setup                                           | A-181          |
| Code Key 39: Axle Capacity                                                  |                |
| Code Key 40: Brake System Types                                             |                |
| Code Keys 41-46: (Obsolete) Reserved for Future Use                         |                |
| Code Key 47: Body Material                                                  |                |
| J J                                                                         |                |

| Code Key 48: Special Body Type Configuration                                         | A-185           |
|--------------------------------------------------------------------------------------|-----------------|
| Code Keys 49-51: (Obsolete) Reserved for Future Use                                  | A-2             |
| Code Key 52: Part Status Code                                                        | A-188           |
| Code Keys 53: (Obsolete) Reserved for Future Use                                     | A-2             |
| Code Key 54: Nominal Voltage                                                         | A <b>-</b> 189  |
| Code Key 55: Current Range                                                           | A <b>-</b> 189  |
| Code Key 56: Electrical Cycles (Hz)                                                  | A <b>-</b> 190  |
| Code Key 57: Electrical Phase                                                        | A <b>-</b> 190  |
| Code Key 58: (Obsolete) Reserved for Future Use                                      | A-2             |
| Code Key 59: Compressor Configuration, Mechanical Refrigeration                      | A <b>-</b> 190  |
| Code Key 60: (Obsolete) Reserved for Future Use                                      | A-2             |
| Code Key 61: Generator Set Type                                                      | A <b>-</b> 191  |
| Code Key 62: Electrical Power Rating                                                 | A <b>-</b> 191  |
| Code Key 63: (Obsolete) Reserved for Future Use                                      | A-2             |
| Code Key 64: Evaporator Mounting Type for Mechanical Refrigeration Units             | A-192           |
| Code Key 65: (Obsolete) Reserved for Future Use                                      | A-2             |
| Code Key 66: Mechanical Refrigeration Configuration                                  | A-192           |
| Code Key 67: Special Features, Mechanical Refrigeration                              | A-193           |
| Code Key 68: Cooling Capacity, Mechanical Refrigeration                              | A <b>-</b> 193  |
| Code Keys 69-72: (Obsolete) Reserved for Future Use                                  | A-2             |
| Code Key 73: Mast Stages, Lift Trucks                                                | A <b>-</b> 194  |
| Code Key 74: Lift Capacities (Pounds)                                                | A-195           |
| Code Keys 75: (Obsolete) Reserved for Future Use                                     | A <b>-</b> 2    |
| Code Key 76: Reason for Delay                                                        | A <b>-</b> 196  |
| Code Key 77: Kingpin Setting                                                         | A <b>-</b> 197  |
| Code Key 78: Trailer Width                                                           | A-197           |
| Code Key 79: Position Codes                                                          | A <b>-</b> 198  |
| Code Key 80: Severity of Service                                                     | A-202           |
| Code Key 81: Type of Claim                                                           | A-204           |
| Code Key 82: Operator Vehicle / Equipment Condition Report                           | A-204           |
| Code Key 83 Claim Response Reason Code                                               | A-208           |
| Code Key 84 Claim Response Status Code                                               | A-209           |
| VMRS Instruction Set 1: Engine Type Code                                             | A <b>-</b> 210  |
| VMRS Instruction Set 2: Transmission Configuration Code                              | A <b>-2</b> 10  |
| VMRS Instruction Set 3: Special Body Type Code                                       | A <b>-2</b> 11  |
| VMRS Instruction Set 4: Axle (Powered) Type Code                                     | A <b>-2</b> 11  |
| VMRS Instruction Set 5: Equipment Type Code (Power Units)                            | A-212           |
| VMRS Instruction Set 6: Equipment Type Code (Trailers and Containers)                | A-212           |
| VMRS Instruction Set 7: Equipment Type Code (Converters)                             | A <b>-2</b> 13  |
| VMRS Instruction Set 8: Electric Motor Code                                          | A <b>-2</b> 13  |
| VMRS Instruction Set 9: Compressor Code                                              | A <b>-</b> 214  |
| VMRS Instruction Set 10: Generator Set Code                                          | A <b>-</b> 214  |
| VMRS Instruction Set 11: Evaporator Code                                             | A <b>-</b> 215  |
| VMRS Instruction Set 12: Mechanical Refrigeration Type Code                          | A <b>-</b> 215  |
| VMRS Instruction Set 13: Material Handling Equipment Type Code                       | A <b>-2</b> 16° |
| VMRS Instruction Set 14: Equipment Configuration Code (Vocation/Category/Body Style) | A <b>-2</b> 16  |
| VMRS Instruction Set 15: Standard Repair Operation Code                              | A <b>-</b> 216  |

Appendix IIa: Code Key 32—Component Codes (Alphabetical Order) Appendix IIb: Code Key 32—Component Codes (Numerical Order) Appendix IIIa: Code Key 33—Component Codes (Alphabetical Order) Appendix IIIb: Code Key 33—Component Codes (Numerical Order)

Return this form to: TMC/ATA 950 N. Glebe Road Arlington, VA 22203 FAX: (703) 838-1701 email: tmc@trucking.org

(Please Complete the Following)

| (REQUESTO) | R) |  |  |
|------------|----|--|--|
| - unice    |    |  |  |
| Title:     |    |  |  |
| Company:   |    |  |  |
| Adress     |    |  |  |
| Autress.   |    |  |  |
|            |    |  |  |
| Phone:     |    |  |  |
|            |    |  |  |
| Email:     |    |  |  |

Please Describe Your New Code Request. Attach additional sheets if necessary.

- FOR COMPONENT CODE REQUEST (Code Key 33)—Include a description and/or drawing of the component.
- FOR MANUFACTURER / BRAND CODE REQUEST(Code Key 34)—Include manufacturer/supplier/brand name, address, phone number, etc.
- FOR ALL OTHER CODE REQUESTS—Provide with as much detail as possible.
- VMRS License Holders may request new codes without charge; all others call for licensing options.
- If you have any questions, please call TMC offices at (703) 838-1763.

## VMRS

## **Product Price Sheet**

| Item Number<br>T0??? (Mem)<br>(NonMem) | <b>Description</b><br>VMRS Electronic Catalog License | <b>Quanity</b><br>1<br>1  | <b>Price (\$)</b><br>See Website/Call<br>See Website/Call |
|----------------------------------------|-------------------------------------------------------|---------------------------|-----------------------------------------------------------|
| T0625 (Mem)                            | VMRS Complete Corporate License                       | 1                         | See Website/Call                                          |
| (NonMem)                               | (Multi-User Version, Codes and Handbook)              | 1                         | See Website/Call                                          |
| T0626 (Mem)                            | VMRS Complete Developer License                       | 1                         | See Website/Call                                          |
| (NonMem)                               | (Multi-User Version, Codes and Handbook)              | 1                         | See Website/Call                                          |
| T06XX (Mem)                            | VMRS Complete Distribution License                    | 1                         | See Website/Call                                          |
| (NonMem)                               |                                                       | 1                         | See Website/Call                                          |
| T0612 (Mem)                            | VMRS Implementation Handbook                          | 1                         | 195.00                                                    |
| (NonMem)                               |                                                       | 1                         | 260.00                                                    |
| T0617 (Mem)                            | Printed Code Key 33/34 Inserts                        | 1                         | 75.00                                                     |
| (NonMem)                               | Printed Code Key 33/34 Inserts                        | 1                         | 100.00                                                    |
| T0605 (Mem)                            | VMRS Repair Order Code Wall Chart                     | 10                        | 2.50 each                                                 |
|                                        | (25 x 19 size)                                        | 11+                       | 2.00 each                                                 |
| (NonMem)                               | VMRS Repair Order Code Wall Chart                     | 10                        | 3.33 each                                                 |
|                                        | (25 x 19 size)                                        | 11                        | 2.67 each                                                 |
| T0608 (Mem)                            | VMRS Repair Order Code Wall Chart                     | 10                        | 1.50 each                                                 |
|                                        | (8.5 x 11 size)                                       | 11+                       | 1.25 each                                                 |
| (NonMem)                               | ) VMRS Repair Order Code Wall Chart                   | 10                        | 2.00 each                                                 |
|                                        | (25 x 19 size)                                        | 11+                       | 1.67 each                                                 |
| T0610 (Mem)                            | Repair Order Log (Form 20)                            | 100<br>200<br>500<br>1000 | 24<br>46<br>110<br>200                                    |
| (NonMem)                               | Repair Order Log (Form 20)<br>(Two-Part Form)         | 100<br>200<br>500<br>1000 | 32<br>61<br>147<br>267                                    |
| T0611 (Mem)                            | Repair Order Log (Form 21)<br>(One-Part Form)         | 100<br>200<br>500<br>1000 | 21<br>36<br>75<br>130                                     |
| (NonMem)                               | Repair Order Log (Form 21)                            | 100<br>200<br>500<br>1000 | 28<br>48<br>100<br>173                                    |

**Product Price Sheet** 

| Item N<br>T0606 | <b>lumber</b><br>(Mem) | <b>Description</b><br>Repair Order (Form 6) | <b>Quanity</b><br>100<br>200<br>500<br>1000 | <b>Price (\$)</b><br>30<br>50<br>95<br>150 |
|-----------------|------------------------|---------------------------------------------|---------------------------------------------|--------------------------------------------|
|                 | (Non-Mem)              | Repair Order (Form 6)                       | 100<br>200<br>500<br>1000                   | 40<br>67<br>127<br>200                     |
| T0607           | (Mem)                  | Special Repair Order (Form 7)               | 100<br>200<br>500<br>1000                   | 30<br>50<br>95<br>150                      |
|                 | (NonMem)               | Special Repair Order (Form 7)               | 100<br>200<br>500<br>1000                   | 40<br>67<br>127<br>200                     |
| T0604           | (Mem)                  | Repair Order Continuation (Form 13)         | 100<br>200<br>500<br>1000                   | 18<br>30<br>60<br>90                       |
|                 | (NonMem)               | Repair Order Continuation (Form 13)         | 100<br>200<br>500<br>1000                   | 24<br>40<br>80<br>120                      |
| T0609           | (Mem)                  | Equipment File (Form 30)                    | 1-99<br>100+                                | 1.00 each<br>.75 each                      |
|                 | (NonMem)               | Equipment File (Form 30)                    | 1-99<br>100+                                | 1.33 each<br>1.00 each                     |
| T0603           | (Mem)                  | Equipment File Inserts (Form 31)            | 1-99<br>100+                                | .50 each<br>.30 each                       |
|                 | (NonMem)               | Equipment File Inserts (Form 31)            | 1-99<br>100+                                | .67 each<br>.40 each                       |
| T0613           | (Mem)                  | Equipment Master Record (Form 1)            | 100<br>200<br>300<br>400<br>500             | 39<br>76<br>99<br>128<br>150               |

## **Product Price Sheet**

| Item Number  | Description                                    | Quanity    | Price (\$)  |
|--------------|------------------------------------------------|------------|-------------|
| (NonMem)     | Equipment Master Record (Form 1)               | 100        | 52          |
|              |                                                | 200        | 101         |
|              |                                                | 300        | 132         |
|              |                                                | 400        | 171         |
|              |                                                | 500        | 200         |
| T0614 (Mem)  | Equipment Master Record (Form 2)               | Same as T( | 0613        |
| (NonMem)     | Equipment Master Record (Form 2)               | Same as T  | 0613        |
| T0615 (Mem)  | Equipment Master Record (Form 3)               | Same as T( | 0613        |
| (NonMem)     | Equipment Master Record (Form 3)               | Same as T  | 0613        |
| T0616 (Mem)  | Equipment Master Record (Form 4)               | Same as T( | 0613        |
| (NonMem)     | Equipment Master Record (Form 4)               | Same as T( | 0613        |
| T00050 (M    |                                                | 4          | <b>0100</b> |
| 10925? (Mem) | Certified VMRS Specialist Credential Testing   | 1          | \$100       |
| (NonMem)     | Certified VIVIRS Specialist Credential Testing | 1          | \$125       |

## Welcome to VMRS<sup>™</sup>!

This handbook is designed to help motor carriers, software designers, information specialists and industry suppliers implement the Vehicle Maintenance Reporting Standards (VMRS)—*the* industry standard coding convention for tracking equipment and maintenance information. This book provides an outline of VMRS, its advantages to equipment users and industry suppliers, and guidance on the basic implementation requirements.

The development of VMRS began in 1969, undertaken jointly by the Maintenance Committee of the Regular Common Carriers Conferof VMRS—updating this dynamic standard to meet motor carrier and industry supplier needs. In 1997, The Maintenance Council (TMC) of American Trucking Associations became custodian of VMRS, embarking on a thorough review of VMRS at the commercial vehicle industry's request. VMRS <sup>TM</sup> Version 2.0 is *the* latest version of this successful standard. In 2001, TMC expanded its mission to include information technology and logistics, becoming the Technology & Maintenance Council. In 2020, TMC diversified its licensing program, introducing new options such as its VMRS Electronic Catalog and VMRS Complete license packages.

ence, the National Accounting and Finance Council, and the Management Systems Committee of American Trucking Associations (ATA). The Union 76 Division of Union Oil of California through its participation in the ATA Foundation sponsored the initial VMRS study. The VMRS Committee's report was published in 1970, and its recommen-

VMRS <sup>TM</sup> is a universal coding language that can be implemented successfully by any industry which must track the costs of maintaining and operating equipment. The development of VMRS<sup>™</sup> is owed in large part to the volunteer efforts of many segments of the equipment maintenance industry. Thanks to the work of many dedicated individuals, VMRS<sup>™</sup> is a universal coding system that can be implemented successfully by any industry which must maintain

and operate equipment — whether it be trucking, transit, off-road, agricultural, or utility operations.

The ultimate utility and application of VMRS<sup>™</sup> is limited only by the creativity of the user. Welcome onboard!

Robert M. Branck

dations to the industry — establishing a stan-

dard coding convention for universally tracking

equipment and maintenance costs and functions — were approved and adopted by the Executive

Committee of American Trucking Associations

in October 1970. Since 1970, American Trucking

Associations has served as the official custodian

Robert M. Braswell Executive Director Technology & Maintenance Council

Jack Poster VMRS Services Manager Technology & Maintenance Council

## 1. An Introduction to VMRS<sup>™</sup>

#### What is VMRS?

Since 1970, the purpose of VMRS has been to provide a vital communication link between maintenance personnel, computers, and management. It establishes a "universal" language for fleets, original equipment manufacturers' (OEMs), industry suppliers, computers, and those people whose responsibility it is to specify, purchase, operate, and maintain equipment.

Developed by and for equipment users under the auspices of American Trucking Associations, VMRS provides the discipline necessary for different industry segments to communicate with each other. VMRS is the shorthand of maintenance reporting, eliminating the need for extensive written communications with all the inherent problems of miscommunication normally associated with the written word.

To meet the ever-changing needs of the equipment industry, the Technology & Maintenance Council (TMC) of American Trucking Associations serves as the official custodian of VMRS. TMC provides OEMs, manufacturers, part suppliers, and equipment users with updated codes on an "as needed" basis reflective of current equipment design and the informational needs of the VMRS user.

VMRS<sup>™</sup> Version 2.0 is the latest version of the VMRS coding convention, established more than 45 years ago. Since its inception, VMRS has a undergone a significant evolution. Based on user requests, TMC has:

 Expanded Code Key 31 to accommodate an ever-increasing interest in the unique reporting needs of the "off-highway" or "stationary equipment" market. As a result, TMC has made full use of the expanded three-digit code so that these equipment types are addressed. For example, System Code (X6X) has been created to accommodate "equipment dependent attachments." The introduction of this system allows users to track the expense associated with major attachments (those that warrant their own asset number) that are only operational when attached to a "host" piece of equipment (i.e. a truck mounted snow blower, or perhaps a plow).

- Increased the total number of codes in Code Key 33, "Component Codes" to more than 34,000.
- Added Code Key 23, which covers tire position codes; Code Key 24, covering maintenance status codes; Code Key 83, which covers claim response reason, and Code Key 84, which covers claim response status.
- Expanded to Code Key 15, "Work Accomplished" and Code Key 18, "Technician Failure Code" to satisfy customer demands.
- Expanded Code Key 34, which is used to identify more than 11,000 manufacturers, suppliers, and brands.
- Expanded Code Keys 1, 2, 10 and 48, which describe equipment vocations, categories and body types. These codes now accommodate many industries beyond trucking, such as transit, off-highway and construction industries.
- Instituted a Certified VMRS Specialist program to recognize proficiency in VMRS nomenclature, structure, and usage.
- Diversified the VMRS<sup>™</sup> licensing offerings to encourage consistent and appropriate industry use of VMRS.
- Developed customized VMRS training options for in-person and virtual learning.
- Applied VMRS to industry benchmarking programs, such as the TMC/FleetNetAmerica Vertical Roadside Breakdown Benchmarking Program.

#### A Structured Coding System

VMRS is a structured coding system, providing the discipline necessary to operate in today's computer-based information age or — where desired — as a completely manual system. Simple in concept, VMRS can be used at any level, from total operating systems down to the individual part level. The level of coding used is entirely up to the user. One can select the level of reporting detail at any time without the need to redesign the coding structure or implement costly new programs. No matter which level the user selects, the data collected can be compared directly to data collected by others at the same or higher VMRS coding level.

The coding structure encompasses most equipment found within today's transportation activities including trucks, tractors, trailers, forklifts, shop equipment, off-road vehicles, utility vehicles, etc.

#### **Recognized Internationally**

Today, equipment users worldwide use VMRS to capture and report their equipment maintenance activities. Equipment manufacturers and maintenance software suppliers use VMRS coding for parts, thus providing additional impetus for fleets to adopt this universal coding scheme.

A complete service industry has grown up around VMRS, with a number of firms offering VMRS computerized reporting systems and/ or services to fleets. This manual will help your software provider utilize VMRS to your mutual benefit.

#### **15 Distinct Advantages to VMRS**

There are 15 distinct advantages to using VMRS:

- 1. VMRS is Easy to Use—VMRS was designed for use at the shop level. Accurate and easily understood reporting by the mechanic is essential if any information system is to succeed. At the higher level, management must understand what the mechanic has accomplished. VMRS meets both criteria.
- 2. VMRS is Cost Effective—TMC has undertaken the initial cost normally associated with developing such a system. The practicality of the system has been proven, in that VMRS has been in continuous use since 1970. TMC keeps the system dynamic, thus eliminating the need for individual users to continually research and update their systems.
- 3. Follows Accepted Accounting Practices—The VMRS code structure al-

lows the user to comply with the needs of most recognized accounting disciplines. VMRS provides the flexibility to properly massage data to meet both immediate and long-term needs.

#### 4. VMRS Enables Sound Budgeting—

VMRS provides a sound basis for budget preparation and forecasting based on fleet mix, projected utilization, and historic performance. Requests for additional mechanics, increased parts inventory, special equipment, or expanded facilities can readily be supported by data captured using VMRS. VMRS is invaluable in determining how many pieces of equipment are required to support a given workload. The same data can be used to determine the mechanic/parts mix required to support various equipment mixes and utilization criteria.

5. VMRS Helps Control Costs—VMRS provides detailed records of the maintenance activity comprising both equipment and facilities. It identifies where monies were spent, at which point in the life of a piece of equipment repairs were performed, and details the expenses incurred in the supporting activity. Distribution between parts and labor is an inherent part of the VMRS reporting structure, thus allowing analysis of what occurred and when. This is important in determining the cause-and-effect relationship of maintenance.

#### 6. VMRS Improves Facility

Management—VMRS provides the ideal basis for establishing a facility management program. The coding structure provides the basis for complete labor and material distribution, direct and indirect, thus allowing management the opportunity to analyze in detail each cost segment. With this information, management can take whatever action is deemed appropriate to correct those situations which appear out of line. This information provides the necessary input for most purchasing decisions.

7. VMRS Tracks Labor Distribution—VMRS provides complete labor distribution cover-

ing both direct and indirect labor.

- VMRS Helps Control Parts Inventory

   –VMRS was developed, and is used within the industry, as the basis of many successful parts inventory control systems. Some fleets have developed their own systems using VMRS, while others utilize off-the-shelf programs designed and built around the VMRS coding structure. VMRS provides complete details as to parts use, thus identifying which part should be inventoried and which should be procured on an "as needed" basis. For those states having an Inventory Tax, VMRS provides documented back-up.
- 9. VMRS Supports Warranty Claims—The VMRS coding structure incorporates the capability to record and isolate those costs normally associated with warranty. Being a universal language, accepted and endorsed by equipment manufacturers and industry suppliers, VMRS provides the ideal audit trail for instituting and supporting warranty claims. New Code Keys have been developed exclusively for warranty, such as Code Key 81 Type of Claim, Code Key 83 Response Reason Code and Code Key 84 Claim Response Status Code.
- 10. VMRS Improves Preventive

Maintenance Programs—VMRS provides the ideal basis for determining the effectiveness of the PM program. Are PMs being performed too often or not often enough? Should PM intervals or their scopes be modified based on specific failures reported through maintenance reporting? What staffing is required to perform PMs? VMRS provides the answers.

#### 11. VMRS Helps Benchmark

**Equipment and Labor Productivity**—The standards provide data necessary for measuring labor productivity. The relationship between direct and indirect labor can be evaluated and changes implemented as needed. Parts/labor ratios can be established that provide the lowest overall maintenance costs. VMRS provides the basis for establishing the economic break-

point between parts replacement and parts repair. Equipment utilization, an important ingredient in transportation, is impacted by maintenance. VMRS provides the means for recording downtime and identifying the specific reason for excessive delays.

#### 12. VMRS Helps Benchmark

**Component Performance**—VMRS provides the data for measuring performance and reliability of specific components and/or parts. A determination can be made of first failure (normally attributed to the equipment manufacturer) and subsequent failure (normally attributed to maintenance).

#### 13. VMRS Assists in Equipment

**Replacement Decisions**—VMRS can substantiate requests for new or replacement equipment based on current rather than historic information. Maintenance support requirements can be determined for each class of equipment being operated. This allows management to quickly determine whether it is more economical to replace or repair and what support is required in the way of labor and material for any combination of new and/or used equipment.

- **14. VMRS Satisfies Reporting Requirements**—VMRS allows fleets to fulfill the ever-changing reporting requirements dictated by government agencies.
- **15. VMRS-Compatible Software is Widely Available**—Many software suppliers currently offer complete turnkey VMRSbased maintenance programs. Many of these can provide custom-made reports to suit the specific needs of the user. Software is also available from a number of sources allowing in-house processing of VMRS.

#### VMRS<sup>™</sup> Version 2.0 Licensing

#### **Description of Licensing Agreements**

There are four levels of licensing agreements associated with the use of VMRS <sup>TM</sup> Version 2.0:

- Electronic Catalog
- VMRS Complete Corporate
- VMRS Complete Developer
- VMRS Complete Distribution

These license products are delivered in electronic format via download and are updated on a regular basis. Each of these license options have a term of one-year, which is renewable.

Let's examine each of the four to understand how they apply to your organization.

#### A. Electronic Catalog

"VMRS Electronic Catalog" is an annual subscription license that includes VMRS Code Keys 31, 32 & 33 (System/Assembly/Component), along with Code Key 34 (Manufacturer/Supplier/Brand) Codes. "VMRS Electronic Catalog" is intended for use by manufacturers and others seeking to properly identify their specific components with VMRS for use in electronic cataloging and part number matching with a VMRS code. The VMRS Electronic Catalog License includes updates and coding requests at no extra charge. Licensing fee is based on annual company sales (self-reported). License purchases will be reviewed by TMC prior to delivery. The licensee may say that they are VMRS<sup>™</sup> compliant only if they follow the guidelines in the VMRS Implementation Handbook.

#### B. VMRS Complete Corporate License

"VMRS Complete Corporate" is an annual subscription license that includes the complete set of VMRS Code Keys and Instruction Sets. It includes the traditional service and procedural Code Keys that are of value to fleets, service providers and repair facilities. It is to be used internally by the VMRS-license holder, and allows the licensee to import the codes into a software program whose manufacturer holds a VMRS Complete Developer license. The VMRS Complete Corporate License includes updates and coding requests at no extra charge. Licensing fee is based on annual company revenue (self-reported) VMRS License purchases will be reviewed by TMC prior to delivery.

#### *C. VMRS Complete Developer License* "VMRS Complete Developer" is an annual subscription license that limits the use of the VMRS

Code Keys only for the purpose of developing VMRS feature sets (not the VMRS codes) within a developer's own applications or tools. VMRS Code Keys are not distributable with the software or tools. The end-users of the developer's software must individually license the actual VMRS Codes through their own VMRS Complete Corporate license directly from TMC. VMRS License purchases will be reviewed by TMC prior to delivery. The VMRS Electronic Catalog License includes updates and coding requests at no extra charge. The licensee may say that they are VMRS<sup>™</sup> compliant only if they follow the guidelines in the VMRS Implementation Handbook.

#### D. VMRS Complete Distribution License

"VMRS Complete Distribution" is an annual subscription license that includes the VMRS Developer license which also includes the right to distribute the VMRS codes in software or to present the VMRS codes within a Software-as-a-Service (SaaS) offering. Software can be hosted on-premises or cloud-based. Pricing is based on number of end-users, and an annual declaration must be provided by licensee. The VMRS Complete Distribution License includes updates and coding requests at no extra charge. VMRS License purchases will be reviewed by TMC prior to delivery. The licensee may say that they are VMRS<sup>™</sup> compliant only if they follow the guidelines in the VMRS Implementation Handbook.

#### E. Use of the Implementation Handbook

No license is needed / offered. Additional copies of the *VMRS<sup>™</sup> Implementation Handbook* may be obtained from TMC / ATA. (See page 6.)

#### Frequently Asked Questions on VMRS<sup>™</sup> Licensing

- Q. Why does TMC / / ATA require license agreements?
- A. TMC/ATA has always owned proprietary rights in the VMRS system and its trademarks. TMC/ATA uses licensing to make clear how VMRS<sup>™</sup> may be used by members and others. This helps ensure the integrity and utility of the VMRS system, as well as enable TMC/ATA to maintain and enhance the viability of this industry standard.

- Q. Why are there different types of licenses?
- A. Different customers use the VMRS<sup>™</sup> product in different ways. Having different types of licenses, with prices determined by the type of usage, is a fair way to permit appropriate levels of usage by customers.
- Q. Can I make copies of the electronic media and put the materials on my computer network for use by my employees?
- A. All four license versions permit the licensee to copy the electronic media onto an internal network. A licensee may not do share the codes beyond its own company if it holds a VMRS Complete Corporate or Developer License.
- Q. I obtained a copy of the Handbook. Can I type the Code Keys into my own computer?
- A. Purchasing a copy of the Handbook does *not* provide you with the right to create your own electronic database. You may purchase a license to use the electronic media if you want to use the Code Keys on your computer.
- Q. Do I have to use all of the Code Keys?
- A. TMC/ATA does not intend to dictate any particular usage of the VMRS<sup>™</sup> product by members or others. However, a licensee can only say that they or their product are VMRS<sup>™</sup> compliant if they utilize all of the particular Code Key values for the Code Key(s) that they use. If you wish

TMC/ATA to assign a new code not listed in the Code Keys, you may call TMC/ ATA's offices at (703) 838-1763. Licensees may request new codes without charge.

- Q. Can I add my own information to the Code Keys?
- A. TMC/ATA has rights in the Code Keys and in its trademarks, such as VMRS<sup>™</sup>. To maintain the integrity of the Code Keys the significance and good will TMC/ATA has obtained through it's trademarks, TMC/ATA prohibits members who add material to the Code Keys from using any TMC/ATA trademarks in conjunction with the modified material. For example, if you were to add new part numbers to Code Key 33, then you would not be permitted to call it part of the VMRS<sup>™</sup> system. If you wish TMC/ATA to assign a new code not listed in the Code Keys, you may call TMC/ATA at (703) 838-1763.
- Q. Can I distribute copies of the Code Keys to others in the industry?
- A. TMC/ATA does not normally permit distribution of copies of the electronic materials or the Handbook to any entity outside your enterprise. Software containing the Code Keys may be distributed as part of a separate software product under a Distribution License Agreement. Copies of the electronic version may be distributed within your enterprise pursuant to the VMRS Complete Corporate License.

The VMRS<sup>TM</sup> symbol identifies products that use the VMRS<sup>TM</sup> coding convention. Products bearing these logos meet certain minimum criteria set by TMC/ATA as key to using VMRS. For more information, see VMRS <sup>TM</sup> Licensing in Section I of this Handbook.

## Requirements for Using VMRS<sup>™</sup>

#### What Are the Basic Requirements for Implementing VMRS?

All external reporting and data interchange must adhere to VMRS coding conventions as defined herein or further described in this VMRS™ Implementation Handbook.

Internal reporting may use other techniques; however, all external interchange of information must be converted to VMRS using direct correlations. No assumptions, prorations, or averages can be used in any conversions.

Full implementation of VMRS<sup>TM</sup> uses nine key VMRS components. Unless each of the nine items listed below can be checked "yes," the user is not implementing VMRS<sup>™</sup> correctly and will be unable to obtain credible or meaningful direct comparisons from any VMRS data base or other VMRS participant.

#### YES Does the System Do the Following?

- Use the VMRS Equipment Master Record.
- Identify Equipment Vocation — Code Key 1.
- Segregate costs by Reason for Repair— Code Key 14
- Identify work accomplished using VMRS Coding—Code Key 15
- At minimum, identify systems via the three-digit VMRS System Code —Code Key 31
- For more detail, identify assemblies via the three-digit VMRS Assembly Code—Code Key 32
- For even more detail, identify individual parts via the three-digit VMRS Component Code—Code Key 33.
- Identify part/equipment manufacturers, suppliers or brands universally using Code Key 34.
- Have the capability to record VMRS Technician Failure Codes—Code Key 18.

Let's now look at each of these nine VMRS components to see how VMRS works.

#### The Equipment Master Record

What is a piece of equipment? It is not just a year, make, and model, but rather a unique series of components assembled to perform a specific task. Under VMRS, each of these components can be followed and monitored on an independent basis or as a total piece of equipment. The sum of the costs of maintaining the components represents total equipment maintenance cost.

VMRS uses a Equipment Master Record (similar to a birth certificate) to record many of the items appearing on the manufacturer's line set tickets. The Equipment Master Record Form allows for consolidation of data from all manufacturers into a uniform format.

#### Equipment Vocation Codes: Code Key 1

Each piece of equipment must be clearly identified as being assigned to a specific mission, identifiable within the VMRS coding system. To this end, TMC has expanded these codes to meet additional equipment user needs. Using Code Key 1, for example, allows linehaul costs to be identified and separated from pickup and delivery and/or other equipment assignments.

Code Key 1 identifies the primary activity or vocation to which a unit has been assigned— "what the equipment does." Additional codes are available through TMC for those equipment operations that do not fall into the following categories. What follows is a sampling of codes that appear in Code Key 1.

#### Code **Equipment Activity**

- Linehaul (non-refrigerated) 10
- 11 Combination Service (predominately linehaul, non-refrigerated)
- 12 Linehaul (refrigerated)
- Combination Service (predominately 13 linehaul, refrigerated)
- 20 Pickup and Delivery (non-refrigerated)
- 21 Combination Service (predominately pickup and delivery, non-refrigerated) 22
  - Pickup and Delivery (refrigerated)

- 23 Combination Service (predominately
- pickup and delivery, refrigerated)
- 30 Billing and Collecting
- 40 Platform
- 50 Terminal/Warehouse/Plant
- 60 Maintenance
- 80 Insurance and Safety
- 90 General and Administration
- A1 Airport / Airport Support / Ground Support Vehicles
- B1 Construction
- C1 Farm / Agriculture
- D1 Fire Service
- E1 Heavy Haul
- F1 Logging
- G1 Mining
- H1 Oil Field
- L1 Refuse / Recycle Vehicle
- M1 Rescue / Crash Vehicle
- N1 Utility
- P1 Wrecker / Recovery Vehicle
- Q1 Military Vehicle
- S1 Earth Moving/Land Clearing
- T1 Demolition
- U1 Public Transportation
- V1 Construction Redi-Mix
- W1 Feed Mill

Combinations of Code Keys can be used as a numerical sentence to describe various aspects of labor or equipment. For example, Code Keys 1, 2, and 48 can be used together to generate a single code that describes what the equipment does, what it is, and what special body type it has.

"1-10-185" identifies a truck (Code Key 2), used in pickup and delivery service (Code Key 1), with a special walk-in refrigerated van type body (Code Key 48). VMRS<sup>™</sup> calls these numerical sentences "Instructional Sets."

#### Reason for Repair Codes: Code Key 14

Identifying what caused a piece of equipment to come in for repair is essential to proper equipment management. VMRS provides for the segregation of this activity in one of the three following areas:

 Maintenance—This represents all monies spent on equipment to keep it operational, and could be used to affect management's decision to purchase that piece of equipment again. Monies spent in this category directly influence the replacement decision.

- 2. **Management Decision**—This category identifies and isolates all monies spent which are neither the equipment's nor manufacturer's fault and over which management has direct control. An example would be the cost of adding new logos onto a piece of equipment.
- Outside Influence—Those items, over which neither the manufacturer nor the user have direct control, are classified in this category.

Under VMRS, each of the major groupings listed previously is further subdivided into a series of specific "Reason for Repair" codes.

#### Maintenance

- Code Item
- 01 Breakdown
- 02 Consumption, Fuel
- 03 Consumption, Oil
- 04 Driver's Report
- 05 Routine Inspection
- 06 Lubrication
- 07 Pre-Delivery
- 08 PM
- 09 Rework
- 10 Road Call
- 11 Routine
- 12 Noted During PM or Inspection
- 13 No Start
- 18 Wheel-off

#### **Management Decision**

- Code Item
- 21 Capital Improvement
- 22 Conversion
- 23 Modification
- 24 Special Study
- 25 Non-contract

#### **Outside Influence**

- Code Item
- 31 Accident, Non-Reported
- 32 Accident, Reported
- 33 Manufacturer's Recall
- 34 Statutory Inspection
- 35 Statutory Modification
- 36 Theft

| 37      | Vandalism               |
|---------|-------------------------|
| 38      | Warranty                |
| 39      | Natural Causes          |
| 41      | Abuse of Equipment      |
| 42      | Decommissioned/Sold     |
| 43      | Roadside Inspection     |
| 44      | Campaign                |
| 47      | Abuse Caused By Drivers |
| 48      | Goodwill-Manufacturer   |
| Towing  | Theres                  |
| 1 ()(10 | ITAM                    |

| Code | Item                       |
|------|----------------------------|
| 61   | Load Shift / Load Transfer |
| 64   | Driver Out of Hours        |
| 65   | Lock-out                   |
| 69   | Secure/Storage Impound     |
|      |                            |

#### Work Accomplished Codes: Code Key 15

Classifying the work performed by the mechanic is important. For example, there is considerable difference between inspecting, adjusting, or repairing brakes. The original VMRS Codes Committee determined, and rightfully so, that use of such terms as major and minor would not suffice, as these terms left too much interpretation to the user. As a result, a series of two-digit work accomplished codes were developed. Each code specifically identifies what work was accomplished by the mechanic at the time the work was performed. The codes are briefly summarized below:

| Code | Work Accomplished     |
|------|-----------------------|
| 01   | Adjust                |
| 02   | Clean                 |
| 03   | Replace New           |
| 04   | Replace Rebuilt       |
| 05   | Replace Used          |
| 06   | Inspect               |
| 07   | Lubricate             |
| 08   | Overhaul              |
| 09   | Troubleshooting       |
| 13   | Other Maint. Repair   |
| 14   | Install               |
| 15   | Paint Prep, & Repaint |
| 17   | Add Fluids            |
| 18   | Road Test             |
| 19   | Rewire / Wire         |
| 20   | Towing                |
| 21   | Fabricate/Weld/Burn   |
| 24   | Repair                |
|      |                       |

- 25 Remove
- 30 Work Incomplete
- 31 Rotate
- 32 Torque
- 33 Tighten
- 44 Flush
- 51 Rebuild
- 58 Diagnose
- 98 In Frame Overhaul
- 99 Out of Chassis Overhaul
- A PM Level A
- B PM Level B
- C PM Level C
- D PM Level D
- E PM Level E
- F PM Level F
- G PM Level G
- H PM Level H
- O PM Level O

#### VMRS System Level Codes: Code Key 31

VMRS<sup>™</sup> uses a series of three-digit descriptor codes that readily and consistently identify the specific systems involved. While these codes are the heart of the "common language" of VMRS and are a vital part of the VMRS concept, they are by themselves nothing more than coding conventions designed for use at all levels within the industry, from fleets to mechanics to manufacturers to suppliers of parts. For example, brakes are identified as a system by Code Key 31 System Code 013.

A brief listing of Code Key 31 codes follows:

### Cab, Climate Control, Instrumentation and Aerodynamic Devices

Code System

- 001 Air Conditioning, Heating, and Ventilating System
- 002 Cab and Sheet Metal
- 003 Instruments, Gauges (All), and Meters
- 004 Aerodynamic Devices

#### Chassis

- 011 Axles Front—Non-Driven
- 012 Axles Rear—Non-Driven
- 013 Brakes
- 014 Frame
- 015 Steering
- 016 Suspension

| 017 | Tires<br>Wheels Rim Llubs and Rearings | 056 |
|-----|----------------------------------------|-----|
| 018 | Automatic/Manual Chassis Lubricator    | 057 |
| 111 | Undercarriage                          | 059 |
| 112 | Stabilization                          | 151 |

#### Drivetrain

- 021 Axle Driven—Front Steering
- 022 Axle Driven—Rear
- 023 Clutch
- 024 Drive Shaft(s)
- 025 Transfer Case
- 026 Transmission—Main, Manual
- 027 Transmission—Main, Automatic028 Transmission—Auxiliary and Transfer
- Case 029 Auxiliary Section (Transmission—
- Main, Manual)
- 121 Final Drive

#### Electrical

| Code | System                           |
|------|----------------------------------|
| 031  | Charging System                  |
| 032  | Cranking System                  |
| 033  | Ignition System                  |
| 034  | Lighting System                  |
| 036  | Supplemental Information Devices |
| 037  | Modules/Relays - Electrical      |

#### Engine / Motor Systems

- 041 Air Intake System
- 042 Cooling System
- 043 Exhaust System
- 044 Fuel System
- 045 Power Plant
- 046 Electric Propulsion System
- 047 Filter Kits (Multi-piece)
- 048 Powertrain-Electric, Hybrid
- 141 Hydrogen Fuel Cell
- 142 LNG Engine Fuel System
- 143 CNG Engine Fuel System

#### Accessories

- 051 General Accessories (for power units, trailers, etc.)
- 052 Electrical Accessories (for power units, trailers, etc.)
- 053 Expendable Items (for power units, trailers, etc.)
- 054 Horns and Mounting and Reverse Signal Alarms
- 055 Cargo Handling, Restraints and Lift Systems (for power units, trailers, etc.)

- Power Take Off
- 057 Spare Wheel Mounting
- 058 Winch (for power units, trailers, etc.)
- 059 Vehicle Coupling
- 151 Auxiliary Power Unit (APU)
- 152 Onboard Lavatory
- 153 Stationary Generator
- 154 Medical Devices

#### **Equipment Dependent Attachments**

- 061 Terminal Equipment Systems and Accessories
- 063 Satellite Communications Systems
- 065 Hydraulic Systems, Multifunctional
- 066 Scrapping
- 067 Buckets
- 068 Lifting
- 069 Conveyance
- 161 Sweeping
- 162 Spreading
- Chipping
- 164 Blowing
- 165 Vacuuming
- 166 Trenching
- 167 Tilling
- 168 Mowing
- 169 Ripping
- 261 Raking
- 262 Breaking
- 263 Hammering
- 264 Grappling
- 265 Magnetic
- 267 Drilling and Boring
- 268 Pulling
- 269 Dust & Debris Collecting
- 362 Weighing & Measuring
- 364 Paving
- 369 Crushing
- 465 Compacting

#### **Bodies and Vessels**

- 071 Body (except bulk carrier body)
- 072 Rear Wall and Door
- 073 Tank Vessel, inner shell
- 074 Tank Vessel, outer jacket
- 075 Manholes
- 076 Rings and Bolsters
- 077 Trailer Frame and Support
- 078 Trim and Miscellaneous Hardware
- 079 Safety Devices
- 171 Mixers
- 172 Compaction Bodies

- 173 Tilt Bodies
- 174 Bus Body
- 175 Emergency Vehicle
- 177 Recreational Vehicle

#### Heating and Refrigeration

- 081 Heating Unit (for power units, trailers, etc.)
- 082 Refrigeration, Mechanical (for power units, trailers, etc.)
- 083 Refrigeration, Nitrogen (for power units, trailers, etc.)
- 084 Refrigeration, Holdover Plate (for power units, trailers, etc.)

#### **Bulk Product Transfer Systems**

- 091 Blowers, Conveyors, and Vibrators (for power units, trailers, etc.)
- 092 Compressor, Bulk Product Systems (for power units, trailers, etc.)
- 094 Engine, Auxiliary (for power units, trailers, etc.)
- 095 Manifold (for power units, trailers, etc.)
- 096 Power Shaft (for power units, trailers, etc.)
- 097 Pump (for power units, trailers, etc.)
- 098 Valves and Controls (for power units, trailers, etc.)
- 099 Safety Devices, Instruments and Gauges (for power units, trailers, etc.)
- 191 Bulk Storage System
- 192 Batch Mobile Processing Plant
- 193 Belt Conveyor System
- 194 Bucket Conveyor System
- 195 Screw Conveyor System
- 196 Roller Conveyor System
- 197 Chain Conveyor System
- 198 Paddle Wagon, Drag Chain Assembly
- 199 Processing Screens
- 291 Dairy Pumping Unit
- 292 Concrete Pumping Equipment
- 293 Oil Shaker Box
- 294 Fuel Metering

#### Assembly Level Codes: Code Key 32

Through the use of assembly level codes, VMRS provides additional capability to further define Code Key 31's System Codes. The first classification below the system level is referred to as

the assembly. At this level, all major groupings within each system are broken out and reported through the use of a three digit code. These, when used with their system prefix, identify the specific assembly within a piece of equipment. For example, front brakes and drums can be identified by a combination of the System and Assembly Code 013-001. A complete listing of Code Key 32 appears elsewhere in this *Handbook*.

#### Component Level Codes: Code Key 33

In order to provide a common generic term for each part within a piece of equipment, the system and assembly codes are further subdivided to the component level. This is accomplished through the use of an additional three digit part identifier code. These codes should not be confused with the manufacturers' or suppliers' unique identification (part) numbers, but rather should be considered universal identifiers or generic terms for the part. For example, a front brake lining can be identified by the following combination of System/Assembly/Component codes—013-001-015. A complete listing of Code Key 33 appears elsewhere in this *Handbook*.

#### Manufacturer/Supplier/Brand Identification: Code Key 34

In order not to disturb either the manufacturers' or suppliers' unique numbering system, VMRS uses its own generic means of identifying manufacturers/suppliers or their brands. The identifier is a five-character alpha code, assigned by TMC.

It used as a prefix to the manufacturers' and/or suppliers' unique number. It is not the intent of VMRS to supplant the manufacturers'/suppliers' unique part numbering systems, but rather to supplement them.

When a Code Key 34 manufacturer's (or brand) code and part number are used in conjunction with the VMRS System/Assembly/Component level codes (Code Key 33), precise identification of a specific part is possible on a universal basis. This commonality of identification on a consistent basis is a prerequisite to developing an industry database for analysis of maintenance information or for mutually exchanging information on a meaningful basis. A complete listing of Code Key 34 appears elsewhere in this *Handbook*.

#### Technician Failure Codes: Code Key 18

VMRS has the additional capability of identifying why a mechanic or supervisor thinks a part failed and why. It is a two-character alpha-numeric code.

An example of a technician part failure code is: 22 = Part Misaligned.

Code Key 18 is listed briefly below:

| Code | Description                         |
|------|-------------------------------------|
| 00   | No Failure                          |
| 01   | Battered, Hammered                  |
| 02   | Burned, Scorched, Melted, Blistered |
| 03   | Crushed, Pinched, Folded, Crimped   |
| 04   | Dented                              |
| 05   | Elongated, Stretched                |
| 06   | Faded, Dulled Finish                |
| 07   | Improper Fluid Level                |
| 08   | Improper Electrical Value           |
| 09   | Insufficient Clearance, Rubs        |
| 10   | Bent                                |
| 11   | Binds, Sticks                       |
| 12   | Broken                              |
| 13   | Chipped, Pitted                     |
| 14   | Cracked                             |
| 15   | Foreign Material Present            |
| 16   | Glazed                              |
| 17   | Insufficient Lubrication            |
| 18   | Leaking                             |
| 19   | Loose                               |
| 20   | Lubrication or Oil Soaked           |
| 21   | Misadjusted                         |
| 22   | Misaligned                          |
| 23   | Not Connected                       |
| 24   | Not Drilled                         |
| 25   | Out of Balance                      |
| 26   | Out of Round                        |
| 27   | Overheated                          |
| 28   | Part Improperly Installed           |
| 29   | Part Omitted                        |
| 30   | Poor Fit, Wrong Size                |
| 31   | Poor Metal Finish                   |
| 32   | Porosity                            |
| 33   | Registers Incorrectly               |
| 34   | Rough                               |

35 Rusted or Corroded 36 Scored or Scratched 37 Seized 38 Shorted 39 Soiled or Stained 40 Stripped / Cross Threaded 41 Torn, Punctured or Split 42 Warped, Twisted 43 Weak 44 Worn 45 Wrong Part 46 Lost or Missing 47 High Pressure 48 Low Pressure 49 Cut or Rubbed 50 Hard or Brittle 51 Inoperative 52 Leaking Air 53 Leaking Compression 54 Leaking Exhaust 55 Leaking Fuel 56 Leaking Oil 57 Leaking Refrigerant 58 Leaking Water 59 Moisture, Condensation 60 Noisy Oil Passing 61 62 Improper Fabrication 63 Improper Weld 64 Plugged 66 Vibration 67 Spun 68 Brightwork/Chrome Defect 69 Insufficient Ground 70 Underspray 71 Overspray 72 Peeled, Flaked, Bubbled 73 Orange Peel 74 Runs, Sags 75 Thin Paint or Unpainted 80 Underinflated 81 Flat 82 Needs Repair 83 Mismatched Height/Tread 84 Irregular Wear 85 Curbed Brake Skid 86 87 Chain Damage 88 Vehicle Mechanical Damage 94 Leaking Coolant 95 Reprogram 96 Primer Peeling from Part

- 97 Paint Peeling from Primer
- 98 Wrong Color
- 99 Replaced Before Failure
- A1 Campaign
- A2 Leaking Diesel Exhaust Fluid (DEF)
- A9 Improper Torque
- B1 Blowout
- B2 Contamination

#### Summary

In summary, there are nine basic, integral parts to VMRS<sup>™</sup>, each interrelated to the other. Independently they cannot be considered VMRS any more than a chassis by itself can be considered a truck. VMRS, by its very concept, requires complete integration of all elements in the same manner that all parts of a piece of equipment must be considered when reviewing the entire piece of equipment. The basic VMRS elements are:

- 1. The VMRS Equipment Master Record—an equipment birth certificate.
- Code Key 1: Equipment Vocation Codes used to identify the specific work assignment of the piece of equipment.

- 3. Code Key 14: Reason for Repair Codes used for segregating repair expenditures.
- Code Key 15: Work Accomplished Codes—used to denote what tasks were performed to the piece of equipment.
- Code Key 31: System Level Coding—used to identify equipment systems.
- Code Key 32: Assembly Level Coding used to identify equipment subsystems.\*
- Code Key 33: Component Level Coding used to identify equipment components.\*

\*SPECIAL NOTE: If coding to the assembly or part level is exercised, no substitution or deviation of coding structure is permitted.

- Code Key 34: Manufacturer/Supplier/ Brand Code—used to identify the actual manufacturer/supplier or brand of a given part.
- Code Key 18: Technician Failure Code used to record the technician's/supervisor's best estimate as to why a specific component failed.

## 3. How to Implement VMRS<sup>™</sup>

This section provides guidelines for implementing VMRS<sup>™</sup>. While general in nature, the procedures and recommendations discussed herein are based upon proven procedures and equipment user experience representing a variety of fleet types and sizes. Whether or not you choose to implement VMRS directly, or through an outside vendor, this section should provide useful guidance in managing and streamlining the implementation process.

How you — the equipment user — choose to implement VMRS beyond the basic requirements is a matter of individual management judgement. However, following these guidelines increases your chances of making VMRS work for your operation.

The best means of ensuring successful implementation of VMRS is through:

- full management participation during initial implementation,
- adequate training of all personnel in VMRS fundamentals, and;
- action upon the information produced by VMRS.

#### **Implementation Preparation**

A fleet maintenance information system should be one of several equipment history subsystems capable of providing uniform source data and information to all relevant fleet management functions. The principle is simple: data is captured once, then redistributed as needed in appropriate formats. Eliminating duplication minimizes information errors.

Right from the start, all managers who will derive information from VMRS should be involved in the process of determining how the information will be formatted. Top management should support the formation of a implementation committee which will represent appropriate management functions and assist in implementing VMRS. It's important that all members of this committee approach this task free of any preconceived ideas. Finally, one person should be given responsibility and authority to lead this team effort.

There are 17 basic steps to implementing VMRS from scratch. These are:

- Define the company purpose for implementing VMRS.
- 2. Assign a VMRS project manager.
- 3. Designate participating departments.
- 4. Obtain all appropriate VMRS<sup>™</sup> references, such as this *Handbook*.
- 5. Contact and visit fleets currently using VMRS.
- 6. Conduct a systems study of current practices.
- Approve the findings of the systems study from Step 6.
- 8. Develop a VMRS implementation plan.
- 9. Design the new fleet management system around VMRS.
- Develop all necessary data processing system applications (i.e., maintenance management software or paper-based data entry system) either internally, or through an outside supplier.
- 11. Develop/obtain VMRS training materials and support procedures.
- 12. Train all necessary personnel.
- 13. "Beta" test the VMRS system.
- 14. Document VMRS system performance.
- 15. Modify training materials and procedures if necessary.
- 16. Fully implement VMRS.
- Review, evaluate, enhance and expand VMRS usage either continually or periodically.

Failure to follow these 17 steps has proven troublesome for fleets trying to haphazardly implement VMRS. Shortcuts to this process inevitably lead to incomplete and ineffective systems, duplication of work, and systems interface incompatibility. The only way to avoid such waste is through the planned, progressive and orderly development of integrated systems. Let's now examine each of the 17 steps in detail.

## 1. Define the Company Purpose for Implementing VMRS.

This definition should be general in scope, reflecting the goals of what VMRS should ultimately provide the company. This step helps establish a company-wide common objective.

An example of such a purpose statement is:

"The purpose of the Equipment and Maintenance Management Information System is to provide essential information for the future and current procurement, operation, and maintenance of the company's automotive and associated equipment. Uniform financial, usage, and utilization information on individual pieces of equipment, maintenance parts, labor charges, and maintenance facilities should be available to all departments in the detail and format they separately require."

#### 2. Assign a VMRS project manager.

The project manager is the team leader and should be selected with care. This person must have:

- a degree of recognition within the organization,
- time to devote to the project,
- an overall understanding of various departmental functions, responsibilities, and interrelationships, and;
- possess the ability to develop consensus between subordinates, supervisors and peers.

It's a mistake to simply assign this role to the company's data processing manager just because someone expects that this person should design the system.

#### 3. Designate participating departments.

Initially, it may not be possible to designate all participants to the project. However, it is essential to include, as soon as possible, managers from all relevant departments, such as maintenance, accounting, equipment and data processing. Other participants may represent operations, environmental, and safety departments, for example. As the project evolves, participants may be added or removed as needed.

### 4. Obtain all appropriate VMRS<sup>™</sup> references, such as this Handbook.

Since you're reading this you've obviously already purchased the VMRS<sup>™</sup> *Handbook*. Other informative VMRS references are available by calling the Technology & Maintenance Council's customer service line at (866) 821-3468 or (703) 838-1763. You should always check to see that you have the latest codes and materials, as updates are issued frequently.

## 5. Contact and visit fleets currently using VMRS.

If one picture is worth a thousand words, several visits to fleets already using VMRS can be worth many times that. Such visits should be planned so that key project team members can meet with their host fleet's opposites. Feel free to contact TMC staff at (703) 838-1763 for assistance in making such contacts.

## 6. Conduct a systems study of current practices.

A systems study of current practices can reveal a detailed understanding and identification of:

- existing information systems in the company directly or indirectly related or applicable to the equipment and maintenance function and their interrelationships, if any.
- data and information requirements of users of the one or more existing systems which may or may not relate to the new system.
- all prospective users of the new system and data/information requirements.
- sources of data input to the existing system.
- similar data currently being recorded at several points and, similarly, the identification of similar or duplicate reports being prepared and distributed from several uncoordinated sources.

Interviews, reports, and onsite visits may all be necessary during the systems study. Documentation, including appropriate flow charts of data/information, should be included in the report.

A draft should be reviewed by all project members to ensure its effectiveness and accuracy. The