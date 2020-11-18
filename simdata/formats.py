import msgpack
from abc import ABC, abstractproperty, abstractmethod


class FormatBase(ABC):
    @abstractproperty
    def proplist(self):
        pass

    @abstractproperty
    def header(self):
        pass

    @abstractmethod
    def parse(self, msg):
        pass


class G1000(FormatBase):
    def __init__(self):
        self.col_config = (
            ("Lcl Date", "local_date", "#yyy-mm-dd", 10),
            ("Lcl Time", "local_time", "hh:mm:ss", 8),
            ("UTCOfst", "utc_offset", "hh:mm", 7),
            ("AtvWpt", "next_wp", "ident", 6),
            ("Latitude", "lat", "degrees", 12, lambda x: f"{x:12.7f}"),
            ("Longitude", "lon", "degrees", 12, lambda x: f"{x:12.7f}"),
            ("AltB", "alt_indicated", "ft msl", 7, self._2f),
            ("BaroA", "baro", "inch", 5, self._2f),
            ("AltMSL", "alt_msl", "ft msl", 7, self._1f),
            ("OAT", "oat", "deg C", 5, self._1f),
            ("IAS", "ias", "kt", 6, self._2f),
            ("GndSpd", "gs", "kt", 6, self._2f),
            ("VSpd", "vs", "fpm", 7, self._2f),
            ("Pitch", "pitch", "deg", 6, self._2f),
            ("Roll", "roll", "deg", 6, self._2f),
            ("LatAc", "latg", "G", 6, self._2f),
            ("NormAc", "vertg", "G", 6, self._2f),
            ("HDG", "hdg", "deg", 5, self._1f),
            ("TRK", "trk", "deg", 5, self._1f),
            ("volt1", "volts", "volts", 5, self._1f),
            ("FQtyL", "fuel_l", "gals", 6, self._2f),
            ("FQtyR", "fuel_r", "gals", 6, self._2f),
            ("E1 FFlow", "eng1_gph", "gph", 8, self._2f),
            ("E1 OilT", "eng1_oil_temp", "deg F", 8, self._2f),
            ("E1 OilP", "eng1_oil_press", "psi", 8, self._2f),
            ("E1 MAP", "eng1_map", "Hg", 6, self._2f),
            ("E1 RPM", "eng1_rpm", "rpm", 6, self._1f),
            ("E1 CHT1", "eng1_cht", "deg F", 7, self._2f),
            ("E1 EGT1", "eng1_egt", "deg F", 7, self._2f),
            ("TAS", "tas", "kt", 3, lambda x: f"{int(x)}"),
            ("HSIS", "hsi_source", "enum", 4),
            ("CRS", "course", "deg", 7, self._1f),
            ("HCDI", "hcdi", "fsd", 6, lambda x: f"{x:.3f}"),
            ("VCDI", "vcdi", "fsd", 6, lambda x: f"{x:.3f}"),
            ("WndSpd", "wind_spd", "kt", 6, self._2f),
            ("WindDr", "wind_dir", "deg", 6, self._1f),
            ("WptDst", "wp_dist", "nm", 6, self._1f),
            ("WptBRG", "wp_brg", "deg", 6, self._1f),
            ("MagVar", "magvar", "deg", 6, self._1f),
            ("AfcsOn", "ap_master", "bool", 6, lambda x: "1" if x else "0"),
            ("RollM", "roll_mode", "enum", 5),
            ("PitchM", "pitch_mode", "enum", 6),
            ("RollC", "ap_roll_cmd", "deg", 5, self._1f),
            ("PitchC", "ap_pitch_cmd", "deg", 6, self._1f),
        )

    @property
    def proplist(self):
        return [x[1] for x in self.col_config]

    @property
    def header(self):
        metastring = '#airframe_info, log_version="1.00", airframe_name="Beechcraft A36/G36", unit_software_part_number="006-B0319-9C", unit_software_version="11.12", system_software_part_number="006-B0858-08", system_id="", mode=NORMAL,'
        h1 = []
        h2 = []
        for col in self.col_config:
            width = col[3]
            h1.append(col[2].rjust(width))
            h2.append(col[0].rjust(width))
        return f'{metastring}\n{", ".join(h1)}\n{", ".join(h2)}'

    @staticmethod
    def _2f(x):
        return f"{x:.2f}"

    @staticmethod
    def _1f(x):
        return f"{x:.1f}"

    def parse(self, msg):
        msg = msgpack.unpackb(msg)
        output = []
        for col in self.col_config:
            field = col[1]
            width = col[3]
            if len(col) == 5:
                formatter = col[4]
            else:
                formatter = lambda x: x
            try:
                text = msg[field]
                if text == None:
                    text = ""
                output.append(formatter(text).rjust(width))
            except KeyError:
                output.append("".rjust(width))
            except (TypeError, AttributeError) as exc:
                print(f"Skipping message due to error in {field} (={msg[field]})")
                return None

        return ", ".join(output)


class Simple(FormatBase):
    def __init__(self):
        self._columns = (
            "local_date",
            "local_time",
            "utc_offset",
            "lat",
            "lon",
            "alt_msl",
            "ias",
        )

    @property
    def proplist(self):
        return self._columns

    @property
    def header(self):
        return ""

    def parse(self, msg):
        msg = msgpack.unpackb(msg)
        props = []
        for prop in msg:
            if prop in self.proplist:
                props.append(str(msg[prop]))
        return ",".join(props)


class SimpleDict(FormatBase):
    def __init__(self):
        self._columns = (
            "local_date",
            "local_time",
            "utc_offset",
            "lat",
            "lon",
            "alt_msl",
            "ias",
        )

    @property
    def proplist(self):
        return self._columns

    @property
    def header(self):
        return ""

    def parse(self, msg):
        out = {}
        msg = msgpack.unpackb(msg)
        for prop in msg:
            if prop in self.proplist:
                out[prop] = msg[prop]
        return out
