import json
from datetime import datetime, date

import unittest
from unittest import mock

from xmlunittest import XmlTestMixin

from tests.base import TestBaseDB, db

from app.model import AircraftBeacon, AircraftType, Receiver, Device, DeviceInfo, ReceiverCoverage

from app.backend.liveglidernet import rec, lxml
from app.backend.ognrange import stations2_filtered_pl, max_tile_mgrs_pl


class TestDB(TestBaseDB, XmlTestMixin):
    def setUp(self):
        super().setUp()

        # Prepare Beacons
        self.r01 = Receiver(name="Koenigsdf", location_wkt="0101000020E610000061E8FED7A6EE26407F20661C10EA4740", lastseen="2017-12-20 10:00:00", altitude=601, version="0.2.5", platform="ARM")
        self.r02 = Receiver(name="Bene", location_wkt="0101000020E6100000D5E76A2BF6C72640D4063A6DA0DB4740", lastseen="2017-12-20 09:45:00", altitude=609, version="0.2.7", platform="x64")
        self.r03 = Receiver(name="Ohlstadt", location_wkt="0101000020E6100000057E678EBF772640A142883E32D44740", lastseen="2017-12-20 10:05:00", altitude=655, version="0.2.6", platform="ARM")
        db.session.add(self.r01)
        db.session.add(self.r02)
        db.session.add(self.r03)
        db.session.commit()

        self.d01 = Device(address="DD4711", lastseen="2017-12-20 10:00:02")
        self.d02 = Device(address="DD0815", lastseen="2017-12-20 09:56:00")
        db.session.add(self.d01)
        db.session.add(self.d02)
        db.session.commit()

        self.di01 = DeviceInfo(registration="D-4711", competition="Hi", tracked=True, identified=True)
        db.session.add(self.di01)
        db.session.commit()

        self.ab11 = AircraftBeacon(
            name="FLRDD4711",
            receiver_name="Koenigsdf",
            location_wkt="0101000020E6100000211FF46C56ED26402650D7EDC6E94740",
            aircraft_type=AircraftType.GLIDER_OR_MOTOR_GLIDER,
            timestamp="2017-12-20 10:00:01",
            track=105,
            ground_speed=57,
            climb_rate=-0.5,
        )
        self.ab12 = AircraftBeacon(
            name="FLRDD4711",
            receiver_name="Koenigsdf",
            location_wkt="0101000020E6100000806DEA295FED2640347D898BB6E94740",
            aircraft_type=AircraftType.GLIDER_OR_MOTOR_GLIDER,
            timestamp="2017-12-20 10:00:02",
            track=123,
            ground_speed=55,
            climb_rate=-0.4,
            altitude=209,
        )
        self.ab21 = AircraftBeacon(
            name="FLRDD0815",
            receiver_name="Koenigsdf",
            location_wkt="0101000020E6100000F38B25BF58F22640448B6CE7FBE94740",
            aircraft_type=AircraftType.POWERED_AIRCRAFT,
            timestamp="2017-12-20 09:54:30",
            track=280,
            ground_speed=80,
            climb_rate=-2.9,
        )
        self.ab22 = AircraftBeacon(
            name="FLRDD0815",
            receiver_name="Bene",
            location_wkt="0101000020E6100000A5E8482EFFF12640DC1EAA16FEE94740",
            aircraft_type=AircraftType.POWERED_AIRCRAFT,
            timestamp="2017-12-20 09:56:00",
            track=270,
            ground_speed=77,
            climb_rate=-1.5,
            altitude=543,
        )
        db.session.add(self.ab11)
        db.session.add(self.ab12)
        db.session.add(self.ab21)
        db.session.add(self.ab22)
        db.session.commit()

        self.rc11 = ReceiverCoverage(
            location_mgrs_short="32TPU8312", date=date(2017, 12, 20), max_signal_quality=10, max_altitude=1000, min_altitude=600, aircraft_beacon_count=20, device_count=2, receiver=self.r01
        )
        self.rc12 = ReceiverCoverage(
            location_mgrs_short="32TPU8434", date=date(2017, 12, 20), max_signal_quality=10, max_altitude=1000, min_altitude=600, aircraft_beacon_count=20, device_count=2, receiver=self.r01
        )
        self.rc12 = ReceiverCoverage(
            location_mgrs_short="32TPU8434", date=date(2017, 12, 21), max_signal_quality=10, max_altitude=1000, min_altitude=600, aircraft_beacon_count=20, device_count=2, receiver=self.r01
        )
        self.rc21 = ReceiverCoverage(
            location_mgrs_short="32TPU8512", date=date(2017, 12, 20), max_signal_quality=10, max_altitude=1000, min_altitude=600, aircraft_beacon_count=20, device_count=2, receiver=self.r02
        )
        db.session.add(self.rc11)
        db.session.add(self.rc12)
        db.session.add(self.rc21)
        db.session.commit()

    @unittest.skip("broken")
    def test_rec(self):
        data = rec(min_timestamp=datetime(2017, 12, 19, 10, 0), min_online_timestamp=datetime(2017, 12, 20, 10, 0)).encode(encoding="utf-8")

        # Check the document
        root = self.assertXmlDocument(data)
        self.assertXmlNode(root, tag="markers")
        self.assertXpathsOnlyOne(root, ('./m[@a="Koenigsdf"]', './m[@a="Bene"]', './m[@a="Ohlstadt"]'))

        # Check the complete document
        expected = """<?xml version="1.0" encoding="UTF-8"?>
        <markers>
            <m e="0"/>
            <m a="Bene" b="47.7158333" c="11.3905500" d="0"/>
            <m a="Koenigsdf" b="47.8286167" c="11.4661167" d="1"/>
            <m a="Ohlstadt" b="47.6577833" c="11.2338833" d="1"/>
        </markers>
        """.encode(
            encoding="utf-8"
        )

        self.assertXmlEquivalentOutputs(data, expected)

    @unittest.skip("broken")
    def test_lxml(self):
        data = lxml().encode(encoding="utf-8")

        # Check the complete document
        expected = """<?xml version="1.0" encoding="UTF-8"?>
        <markers>
            <m a="47.8280667,11.4726500,_15,xxDD0815,543,09:56:00,245,270,77,-1.5,8,Bene,0,xxDD0815"/>
            <m a="47.8258833,11.4636167,Hi,D-4711,209,10:00:02,3,123,55,-0.4,1,Koenigsdf,DD4711,xxDD4711"/>
        </markers>
        """.encode(
            encoding="utf-8"
        )

        self.assertXmlEquivalentOutputs(data, expected)

    @mock.patch("app.backend.ognrange.datetime")
    def test_stations2_filtered_pl(self, datetime_mock):
        datetime_mock.utcnow.return_value = datetime(2017, 12, 20, 10, 0)

        result = stations2_filtered_pl(start=date(2017, 12, 15), end=date(2017, 12, 25))

        data = json.loads(result)

        stations = data["stations"]
        self.assertEqual(len(stations), 3)
        s1 = stations[0]
        s2 = stations[1]
        s3 = stations[2]

        self.assertEqual(s1["s"], "Bene")
        self.assertEqual(s1["lt"], 47.7158)
        self.assertEqual(s1["lg"], 11.3906)
        self.assertEqual(s1["u"], "D")  # Down, because last beacon > 10min. ago
        self.assertEqual(s1["ut"], "2017-12-20 09:45")
        # self.assertEqual(s1["b"], 0)
        self.assertEqual(s1["v"], "0.2.7.x64")

        self.assertEqual(s2["s"], "Koenigsdf")
        self.assertEqual(s2["lt"], 47.8286)
        self.assertEqual(s2["lg"], 11.4661)
        self.assertEqual(s2["u"], "U")
        self.assertEqual(s2["ut"], "2017-12-20 10:00")
        # self.assertEqual(s2["b"], 0)
        self.assertEqual(s2["v"], "0.2.5.ARM")

        self.assertEqual(s3["s"], "Ohlstadt")

    def test_max_tile_mgrs_pl(self):
        result = max_tile_mgrs_pl(station="Koenigsdf", start=date(2017, 12, 15), end=date(2017, 12, 25), squares="32TPU")

        data = json.loads(result)

        self.assertEqual(data["t"], "32TPU")
        self.assertEqual(data["p"][0], "8312/1")
        self.assertEqual(data["p"][1], "8434/2")

        result = max_tile_mgrs_pl(station="Bene", start=date(2017, 12, 15), end=date(2017, 12, 25), squares="32TPU")

        data = json.loads(result)

        self.assertEqual(data["t"], "32TPU")
        self.assertEqual(data["p"][0], "8512/1")


if __name__ == "__main__":
    unittest.main()
