import pytest
from datetime import datetime
from utils import fetch_title, fetch_stream_url, fetch_episode_pages, \
    fetch_metadata
from yledl import StreamFilters


def test_areena_html5_stream_url():
    streamurl = fetch_stream_url('https://areena.yle.fi/1-787136')

    assert len(streamurl) == 1
    assert '/a.m3u8?' in streamurl[0]


def test_areena_html5_metadata():
    metadata = fetch_metadata('https://areena.yle.fi/1-787136')

    assert len(metadata) == 1
    flavors = metadata[0]['flavors']
    assert len(flavors) >= 5
    assert all(f.get('media_type') == 'video' for f in flavors)
    assert all('bitrate' in f and
               'height' in f and
               'width' in f
               for f in flavors)
    assert metadata[0]['duration_seconds'] == 907
    assert metadata[0]['region'] == 'World'
    assert metadata[0]['publish_timestamp'] == '2021-04-01T00:01:00+03:00'
    assert 'expired_timestamp' not in metadata[0]
    assert len(metadata[0]['description']) > 150


def test_metadata_language():
    meta_fin = fetch_metadata(
        'https://areena.yle.fi/1-403848', meta_language='fin')
    title_fin = meta_fin[0].get('title')
    assert title_fin.startswith('Suomen tie jatkosotaan')

    meta_swe = fetch_metadata(
        'https://areena.yle.fi/1-403848', meta_language='swe')
    title_swe = meta_swe[0].get('title')
    assert title_swe.startswith('Finlands väg till fortsättningskriget')


def test_areena_series_titles():
    titles = fetch_title('https://areena.yle.fi/1-3826480')

    assert len(titles) == 10
    assert all(['Suomi on ruotsalainen' in t for t in titles])


def test_areena_series_urls():
    urls = fetch_stream_url('https://areena.yle.fi/1-3826480')

    assert len(urls) == 10
    assert all(['a.m3u8' in url for url in urls])


@pytest.mark.geoblocked
def test_areena_live_url():
    streamurl = fetch_stream_url('https://areena.yle.fi/tv/suorat/yle-tv1')

    assert len(streamurl) == 1
    assert '.m3u8' in streamurl[0]


@pytest.mark.geoblocked
def test_areena_live_metadata():
    metadata = fetch_metadata('https://areena.yle.fi/tv/suorat/yle-tv1')

    assert len(metadata) == 1
    assert len(metadata[0]['flavors']) >= 1
    assert all(f.get('media_type') == 'video' for f in metadata[0]['flavors'])
    assert metadata[0]['region'] == 'Finland'


def test_areena_html5_clip_title():
    title = fetch_title('https://areena.yle.fi/1-3523087')

    assert len(title) == 1
    assert 'Metsien kätkemä' in title[0]


def test_areena_html5_clip_stream_url():
    streamurl = fetch_stream_url('https://areena.yle.fi/1-3523087')

    assert len(streamurl) == 1
    assert '/a.m3u8?' in streamurl[0]


def test_areena_awsmpodamdipv4_stream_url():
    streamurl = fetch_stream_url('https://areena.yle.fi/1-50875269')

    assert len(streamurl) == 1
    assert '/index.m3u8?' in streamurl[0]


def test_areena_awsmpodamdipv4_metadata():
    metadata = fetch_metadata('https://areena.yle.fi/1-50875269')

    assert len(metadata) == 1
    flavors = metadata[0]['flavors']
    assert len(flavors) >= 1
    assert all(f.get('media_type') == 'video' for f in flavors)
    assert metadata[0]['duration_seconds'] == 257
    assert metadata[0]['region'] == 'World'
    assert metadata[0]['publish_timestamp'] == '2021-06-11T08:40:00+03:00'
    assert 'expired_timestamp' not in metadata[0]
    assert len(metadata[0]['description']) > 150


def test_areena_episode_pages():
    episodes = fetch_episode_pages('https://areena.yle.fi/1-3148871')

    # The first page contains 12 episodes, make sure we get several pages
    assert len(episodes) > 20


def test_areena_season_id():
    # An Areena TV URL can point to either a series or a season.
    #
    # For example, the series page of "Sekaisin" is 1-3430975 and the third
    # season of "Sekaisin" is 1-50570316.
    #
    # Yle-dl downloads all episodes from all seasons no matter which ID is
    # used.
    episodes = fetch_episode_pages('https://areena.yle.fi/1-50570316')

    # The seasons contain 8 to 15 episodes, make sure we get several seasons
    assert len(episodes) > 20


def test_areena_episodes_sort_order():
    metadata = fetch_metadata('https://areena.yle.fi/1-4530023')

    # Should be sorted from oldest to newest
    timestamps = [x['publish_timestamp'] for x in metadata]
    assert len(timestamps) > 1
    assert timestamps == sorted(timestamps)


def test_areena_season_and_episode_number():
    # The episode titles should include S01E01, S01E02, etc.
    expected_episodes = []
    for season in range(1, 3 + 1):
        for episode in range(1, 12 + 1):
            expected_episodes.append(f'S{season:02d}E{episode:02d}')

    metadata = fetch_metadata('https://areena.yle.fi/1-4530023')
    titles = [x['title'] for x in metadata]

    assert len(titles) == len(expected_episodes)
    for title, substring in zip(titles, expected_episodes):
        assert substring in title


def test_areena_latest_episode():
    filters = StreamFilters(latest_only=True)
    metadata = fetch_metadata('https://areena.yle.fi/1-4655342', filters)

    assert len(metadata) == 1

    # The latest episode at the time of writing this test was
    # published on 2021-01-27
    publish_date = datetime.strptime(metadata[0]['publish_timestamp'][:10], '%Y-%m-%d')
    assert publish_date >= datetime(2021, 1, 27)


def test_package_page():
    # This is a "package" type page
    episodes = fetch_episode_pages('https://areena.yle.fi/tv/ohjelmat/30-1774')

    assert len(episodes) > 10
