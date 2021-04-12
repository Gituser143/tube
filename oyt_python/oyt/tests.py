from django.test import TestCase
from oyt.models import Playlist
from oyt.models import User
from oyt.models import Video
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


# Create your tests here.


class PlaylistTestCases(TestCase):
    def setUp(self):
        '''
        Setup required objects for testcase
        '''
        User.objects.create(
            username="test_user",
            password="test_password",
            is_superuser=False,
            first_name="test_first",
            last_name="test_last",
            email="test@test.com"
        )

        User.objects.create(
            username="test_user_2",
            password="test_password",
            is_superuser=False,
            first_name="test_first",
            last_name="test_last",
            email="test2@test.com"
        )

        Playlist.objects.create(
            name="test_playlist_1",
            user=User.objects.get(username="test_user"),
            video_ids=[]
        )

        Playlist.objects.create(
            name="test_playlist_2",
            user=User.objects.get(username="test_user"),
            video_ids=[],
            is_private=True
        )

    def test_playlist_is_private(self):
        '''
        Verify Playlist is public by default
        '''
        p = Playlist.objects.get(name="test_playlist_1")
        self.assertEqual(p.is_private, False)

    def test_private_playlist(self):
        '''
        Verify user cannot access private playlists owned by others
        '''
        u = User.objects.get(username="test_user_2")
        playlists = Playlist.objects.filter(
            Q(is_private=False) | Q(user_id=u.id))
        self.assertEqual(len(playlists), 1)
        self.assertNotEqual(playlists[0].user_id, u.id)

    def test_playlist_video_ids(self):
        '''
        Verify newly created playlist has no videos
        '''
        p = Playlist.objects.get(name="test_playlist_1")
        self.assertEqual(len(p.video_ids), 0)

    def test_playlist_user_delete(self):
        '''
        Verify user deletion removes user owned playlists
        '''
        user_obj = User.objects.get(username="test_user")
        user_obj.delete()
        with self.assertRaises(Exception) as context:
            p = Playlist.objects.get(name="test_playlist_1")

        self.assertTrue('does not exist' in str(context.exception))


class VideoTestCases(TestCase):
    def setUp(self):
        '''
        Setup required objects for testcase
        '''
        User.objects.create(
            username="test_user",
            password="test_password",
            is_superuser=False,
            first_name="test_first",
            last_name="test_last",
            email="test@test.com"
        )

        User.objects.create(
            username="test_user_2",
            password="test_password",
            is_superuser=False,
            first_name="test_first",
            last_name="test_last",
            email="test2@test.com"
        )

        Video.objects.create(
            title="test_video_1",
            description="test_description",
            user=User.objects.get(username="test_user"),
            path="/media/test_video.mp4",
            likes=[]
        )

        Video.objects.create(
            title="test_video_2",
            description="test_description",
            user=User.objects.get(username="test_user"),
            path="/media/test_video.mp4",
            likes=[],
            is_private=True
        )

    def test_video_is_private(self):
        '''
        Verify Video is public by default
        '''
        v = Video.objects.get(title="test_video_1")
        self.assertEqual(v.is_private, False)

    def test_private_video(self):
        '''
        Verify user cannot access private videos owned by others
        '''
        u = User.objects.get(username="test_user_2")
        videos = Video.objects.filter(
            Q(is_private=False) | Q(user_id=u.id))
        self.assertEqual(len(videos), 1)
        self.assertNotEqual(videos[0].user_id, u.id)

    def test_video_likes(self):
        '''
        Verify newly created video has no likes
        '''
        v = Video.objects.get(title="test_video_1")
        self.assertEqual(v.num_likes, 0)

    def test_video_user_delete(self):
        '''
        Verify user deletion removes user owned videos
        '''
        user_obj = User.objects.get(username="test_user")
        user_obj.delete()
        with self.assertRaises(Exception) as context:
            p = Video.objects.get(title="test_video_1")

        self.assertTrue('does not exist' in str(context.exception))


class VideoListTestCases(TestCase):
    def setUp(self):
        '''
        Setup required objects for testcase
        '''
        User.objects.create(
            username="test_user_1",
            password="test_password",
            is_superuser=False,
            first_name="test_first",
            last_name="test_last",
            email="test@test.com"
        )

        User.objects.create(
            username="test_user_2",
            password="test_password",
            is_superuser=False,
            first_name="test_first",
            last_name="test_last",
            email="test2@test.com"
        )

        Video.objects.create(
            title="test_video_1",
            description="test_description",
            user=User.objects.get(username="test_user_1"),
            path="/media/test_video.mp4",
            likes=[]
        )

        id1 = User.objects.get(username="test_user_1").id
        id2 = User.objects.get(username="test_user_2").id

        Video.objects.create(
            title="test_video_2",
            description="test_description",
            user=User.objects.get(username="test_user_1"),
            path="/media/test_video.mp4",
            likes=[id1],
            num_likes=1
        )

        Video.objects.create(
            title="test_video_3",
            description="test_description",
            user=User.objects.get(username="test_user_1"),
            path="/media/test_video.mp4",
            likes=[id1, id2],
            num_likes=2
        )

    def test_recent_video_order(self):
        '''
        Verify Ordering of recent videos
        '''

        u = User.objects.get(username="test_user_1")

        most_recent_videos = Video.objects.order_by(
            '-datetime').filter(Q(is_private=False) | Q(user_id=u.id))

        for i in range(1, len(most_recent_videos)):
            v1 = most_recent_videos[i-1]
            v2 = most_recent_videos[i]
            self.assertLessEqual(v2.datetime, v1.datetime)

    def test_liked_video_order(self):
        '''
        Verify Ordering of liked videos
        '''

        u = User.objects.get(username="test_user_1")

        most_liked_videos = Video.objects.order_by(
            '-num_likes').filter(Q(is_private=False) | Q(user_id=u.id))

        for i in range(1, len(most_liked_videos)):
            v1 = most_liked_videos[i-1]
            v2 = most_liked_videos[i]
            self.assertLessEqual(v2.num_likes, v1.num_likes)
