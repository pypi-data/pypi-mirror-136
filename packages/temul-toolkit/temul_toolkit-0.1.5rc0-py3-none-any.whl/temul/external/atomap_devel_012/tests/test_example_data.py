import temul.external.atomap_devel_012.example_data as ed


class TestExampleData:

    def test_get_detector_image_signal(self):
        s = ed.get_detector_image_signal()
        assert hasattr(s, 'plot')
        s.data[:] = 0
        s1 = ed.get_detector_image_signal()
        assert not (s1.data == 0).any()
