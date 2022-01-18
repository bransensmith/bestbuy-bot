# bestbuy-bot

BestBuy-Auto-Cart
Working as of 1/18/2022 
____________
Requirements

•	Python Packages; Selenium Web Driver; BeautifulSoup4, undetected-chrome driver.

•	Requires Gmail Account with an established App Password. See the link below for details. 
    https://support.google.com/accounts/answer/185833?hl=en

____________
Notes


•	Your BestBuy account email must be the same as your Google email account used for outgoing alerts in info.py.

•	This script only works if your set store location has inventory, future releases may include store options within a set range (250 miles).

•	This script does not auto purchase for sake of simplicity but could be implemented easily if you choose to. 

•	I recommend using a scheduler to run the scripts during weekdays only.
 
____________
About

This Script is designed to run on BestBuy.com and only works on Hot-Items such as Graphics cards, PS5 Consoles, XBOX Consoles, Nintendo Systems, or any other type of limited stock item. 
This Bot looks for website element changes every 5 seconds to determine inventory status (In-stock / out of stock). When an object is found to be in stock, the script will start the Auto-Cart function.

 

How Auto-Cart Works 
The script initially logs into your BestBuy account and then sets the preferred store location to your specified preference in info.py.
Auto-Cart waits for inventory and when it’s found, the Bot enters the item queue following these steps:
 

1.	Waits For verification Element
2.	Enter 2FA check using your attached Gmail account
3.	Retrieves Key from your Email and passes to the email verify Function 

Once the 2FA check has been completed successfully, the script will wait for inventory message updates.
If your select store has available inventory, the item will automatically be added to your cart where you then have 10 minutes to complete your purchase through your mobile app. Otherwise, the Bot will alert you of other conditions.

Website Interactions using Selenium have been built in iterations - meaning with each Hot Item restock I have on average 15 minutes to dig through new HTML pages to find the correct elements and build the necessary function. With each restock, the bot is improved along with its potential error handling capabilities. 




 


 





