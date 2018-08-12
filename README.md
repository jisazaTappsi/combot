# combot
random scripts

1. Install dependencies:
    pip install -r requirements.txt in your shell.

2. Add a settings.ini file, with:

    [settings]
    email=<your email>
    pass=<your pass>
    main_url=<the url>
    coordinate_x=<X coordinate number to give permission>
    coordinate_y=<Y coordinate number to give permission>
    scroll_steps=<number of times it scrolls a page>

Detailed Explanation:

main_url = the main url to scrap
coordinate_x = x coordinate of button to give permission to access chrome as a test user
coordinate_y = y coordinate of button to give permission to access chrome as a test user
scroll_steps = the number of scrolls down taken by the scrapper. More equals more results but some maybe far in hte past

3. Add or remove groups and keywords on groups.txt and keywords.txt respectively

4. Run:
    python3 main.py

5. Check results in "leads.xlsx"
