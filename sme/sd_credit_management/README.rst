
=================
SD Credit Management
=================

Configuration
=============
* User Groups

user -> access right -> Enable "Credit limit and credit limit overrid" to define credit limit on contact

Fields
======
* Total Credit Used = Total Receivable + The amount of Sale Orders confirmed but not yet invoiced + The invoices that are in draft state.
* Credit Hold = Boolean field(True/False)
 
Functionality
=============
If Credit Hold field is True

In Sales
--------
* While choosing the customer in a sales order a warning message is displayed.  The user will not be able to confirm the sales order.
* If "Total Credit Used" is greater than or equal to "Credit Limit", in sales order a warning message is displayed when the customer is selected.  The user is not able to confirm the sales order.
* If the Total Credit Used + sales order amount exceed the credit limit then the user is not allowed to confirm the sales order.
* There is no constraint on the DO based on the credit limit.,

In Delivery Order
-----------------
* The user will not be able to confirm the delivery order or to "Mark As Todo", "Check Availability", "Recheck Availablity", "Force Availability" and "validate".

If Credit Limit is not zero.
      
Credits
=======

Contributors
------------
* Silverdale <silverdaletech.com>

This module is maintained by Silverdale.
