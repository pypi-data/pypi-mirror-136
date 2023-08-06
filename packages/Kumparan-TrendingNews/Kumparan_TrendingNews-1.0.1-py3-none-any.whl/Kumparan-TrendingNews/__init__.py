import requests
from bs4 import BeautifulSoup

# Extract data from Website
def data_extraction():
    try:
        content = requests.get('https://kumparan.com/trending',
                               headers={'Cache-Control': 'private, max-age=0, no-cache'})
    except Exception:
        return print('Fail Requests')

    if content.status_code == 200:
        # Get and assign TrendingNews Title, AuthorName, TimePublished
        soup = BeautifulSoup(content.text, 'html.parser')
        main = soup.find('div', {'class': 'Viewweb__StyledView-sc-1ajfkkc-0 cFmAia'})
        title = main.findChildren('span', {
            'class': 'Textweb__StyledText-sc-1uxddwr-0 eSSwLt CardContentweb__CustomText-sc-1gsg7ct-0 grhZrk'})
        author = main.findChildren('span', {
            'class': 'Textweb__StyledText-sc-1uxddwr-0 gACKQ CardContentweb__NameText-sc-1gsg7ct-1 '
                     'CardContentweb___StyledNameText-sc-1gsg7ct-2 bxUak erbwXr'})
        time = main.findChildren('span', {'class': 'Textweb__StyledText-sc-1uxddwr-0 bQqliI'})
        time = time[2::3]

        i = 0
        tnews = dict()
        for ti, thor, tim in zip(title, author, time):
            num = i + 1
            tnews[f'News {num}'] = {}
            tnews[f'News {num}'][f'Title'] = {}
            tnews[f'News {num}'][f'Author'] = {}
            tnews[f'News {num}'][f'TimePublished'] = {}
            tnews[f'News {num}'][f'Title'] = ti.text
            tnews[f'News {num}'][f'Author'] = thor.text
            tnews[f'News {num}'][f'TimePublished'] = tim.text
            i = i + 1
        return tnews

    else:
        return None

# Show the trending news data
def show_data(result):
    if result is None:
        print('Trending News data is not found')
        return
    for news, data in result.items():
        print(f"\nTrending", news)
        for key in data:
            print(key + ':', data[key])

# Execute the function if run from main
if __name__ == '__main__':
    result = data_extraction()
    show_data(result)
