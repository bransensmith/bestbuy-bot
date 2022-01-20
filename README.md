# bestbuy-bot

BestBuy-Auto-Cart
Working as of 1/20/2022 
____________
Requirements

•	Python Packages; Selenium Web Driver; BeautifulSoup4, undetected-chromedriver.

•	Requires a Gmail account with an established App Password. See the link below for details. 
    https://support.google.com/accounts/answer/185833?hl=en

____________

  [1] = List supported product scraping targets (multiple product URLs)     
 

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
 

1.	Waits for verification element
2.	Enter 2FA check using your attached Gmail account
3.	Retrieves Key from Email and passes it to BestBuy.com 

Once the 2FA check has been completed successfully, the script will wait for inventory message updates.
If your select store has available inventory, the item will automatically be added to your cart where you then have 10 minutes to complete your purchase through your mobile app. Otherwise, the Bot will alert you of other conditions.

Website Interactions using Selenium have been built in iterations - meaning with each Hot Item restock I have on average 15 minutes to dig through new HTML pages to find the correct elements and build the necessary functions. With each restock, the Bot is improved along with its potential error handling capabilities. 

--------------

![proofsmaller](https://user-images.githubusercontent.com/95368430/150418852-c01089c7-b731-468f-9b6e-b4a720d1d3a1.png)


--------------
 

![ps5](https://user-images.githubusercontent.com/95368430/150408625-ea3599c2-6677-41a1-860d-f04133b5f4a3.jpg)
 

--------------



