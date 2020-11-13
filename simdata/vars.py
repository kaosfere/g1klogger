from abc import ABC, abstractproperty
import time


class SimpleVar:
    def __init__(self, variable, name, unit, converter=None, width=None):
        self._name = name
        self._unit = unit
        self._width = width
        self._variable = variable
        self._converter = converter
        self._simvar = None

    def load(self, req):
        self._simvar = req.find(self._variable)

    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._unit

    @property
    def width(self):
        if self._width:
            return self._width
        else:
            return len(self.name)

    @property
    def value(self):
        val = self._simvar.get()
        if self._converter:
            val = self._converter(val)

        return val.rjust(self.width)


class CompoundVar(ABC):
    def __init__(self, name, unit, width=None, converter=None):
        self._name = name
        self._unit = unit
        self._width = width
        self._converter = converter
        self._req = None

    def load(self, req):
        self._req = req

    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._unit

    @property
    def width(self):
        if self._width:
            return self._width
        else:
            return len(self.name)

    @abstractproperty
    def value(self):
        pass


class LocalDate(CompoundVar):
    def load(self, req):
        self._year = req.find("LOCAL_YEAR")
        self._month = req.find("LOCAL_MONTH_OF_YEAR")
        self._day = req.find("LOCAL_DAY_OF_MONTH")

    @property
    def value(self):
        return f"{int(self._year.value):4}-{int(self._month.value):02}-{int(self._day.value):02}"


class UtcOffset(CompoundVar):
    def load(self, req):
        self._offset = req.find("TIME_ZONE_OFFSET")

    @property
    def value(self):
        offset_secs = self._offset.value
        if offset_secs <= 0:
            prefix = "+"
            offset_secs *= -1
        else:
            prefix = "-"
        return f"{prefix}{time.strftime('%H:%M', time.gmtime(offset_secs))}"


class HsiSource(CompoundVar):
    def load(self, req):
        self._nav_select = req.find("AUTOPILOT_NAV_SELECTED")
        self._gps_drives = req.find("GPS_DRIVES_NAV1")

    @property
    def value(self):
        if self._gps_drives.value:
            return " GPS"
        return f"NAV{int(self._nav_select.value)}"


class Course(CompoundVar):
    def load(self, req):
        self._req = req
        self._nav_select = req.find("AUTOPILOT_NAV_SELECTED")
        self._gps_drives = req.find("GPS_DRIVES_NAV1")

    @property
    def value(self):
        if self._gps_drives.value:
            crs = rad_to_deg(self._req.get("GPS_WP_DESIRED_TRACK"))
        else:
            crs = self._req.get(f"NAV_OBS:{int(self._nav_select.value)}")
        return f"{crs:.1f}".rjust(self.width)


class ApRollMode(CompoundVar):
    @property
    def value(self):
        return "NONE"


class ApPitchMode(CompoundVar):
    @property
    def value(self):
        return "NONE"


def c_to_f(x):
    return x * 1.8 + 32


def mps_to_kt(x):
    return x * 1.94384


def rad_to_deg(x):
    return x * 57.2958


def fps2_to_g(x):
    return x * 0.031


def ran_to_f(x):
    return x - 459.67


def psf_to_psi(x):
    return x / 144


def m_to_nm(x):
    return x / 1852


vars = [
    LocalDate("Lcl Date", "#yyy-mm-dd", 10),
    SimpleVar(
        "LOCAL_TIME",
        "Lcl Time",
        "hh:mm:ss",
        lambda x: time.strftime("%H:%M:%S", time.gmtime(x)),
    ),
    UtcOffset("UTCOfst", "hh:mm"),
    SimpleVar("GPS_WP_NEXT_ID", "AtvWpt", "ident", lambda x: x.decode("utf-8")),
    SimpleVar("GPS_POSITION_LAT", "Latitude", "degrees", lambda x: f"{x:12.7f}", 12),
    SimpleVar("GPS_POSITION_LON", "Longitude", "degrees", lambda x: f"{x:12.7f}", 12),
    SimpleVar("INDICATED_ALTITUDE", "AltB", "ft Baro", lambda x: f"{x:.2f}", 7),
    SimpleVar("KOHLSMAN_SETTING_HG", "BaroA", "inch", lambda x: f"{x:.2f}"),
    SimpleVar("PLANE_ALTITUDE", "AltMSL", "ft msl", lambda x: f"{x:.1f}", 7),
    SimpleVar("AMBIENT_TEMPERATURE", "OAT", "deg C", lambda x: f"{x:.1f}", 5),
    SimpleVar("AIRSPEED_INDICATED", "IAS", "kt", lambda x: f"{x:.2f}", 6),
    SimpleVar("GROUND_VELOCITY", "GndSpd", "kt", lambda x: f"{x:.2f}", 6),
    # SimpleVar("GPS_GROUND_SPEED", "GndSpd", "kt", lambda x: f"{mps_to_kt(x):.2f}", 6),
    SimpleVar("VERTICAL_SPEED", "VSpd", "fpm", lambda x: f"{x / 60:.2f}", 7),
    SimpleVar("PLANE_PITCH_DEGREES", "Pitch", "deg", lambda x: f"{rad_to_deg(x * -1):.2f}", 6),
    SimpleVar("PLANE_BANK_DEGREES", "Roll", "deg", lambda x: f"{rad_to_deg(x * -1):.2f}", 6),
    SimpleVar("ACCELERATION_BODY_X", "LatAc", "G", lambda x: f"{fps2_to_g(x):.2f}", 6),
    SimpleVar("ACCELERATION_BODY_Y", "NormAc", "G", lambda x: f"{fps2_to_g(x):.2f}", 6),
    SimpleVar(
        "PLANE_HEADING_DEGREES_MAGNETIC",
        "HDG",
        "deg",
        lambda x: f"{rad_to_deg(x):.1f}",
        5,
    ),
    SimpleVar("GPS_GROUND_MAGNETIC_TRACK", "TRK", "deg", lambda x: f"{rad_to_deg(x):.1f}", 5),
    SimpleVar("ELECTRICAL_BATTERY_BUS_VOLTAGE", "volt1", "volts", lambda x: f"{x:.1f}"),
    # SimpleVar("ELECTRICAL_BATTERY_BUS_VOLTAGE", "volt2", "volts", lambda x: f"{x:.1f}"),
    SimpleVar("FUEL_LEFT_QUANTITY", "FQtyL", "gals", lambda x: f"{x:.2f}", 6),
    SimpleVar("FUEL_RIGHT_QUANTITY", "FQtyR", "gals", lambda x: f"{x:.2f}", 6),
    SimpleVar("ENG_FUEL_FLOW_GPH:1", "E1 FFlow", "gph", lambda x: f"{x:.2f}"),
    SimpleVar("ENG_OIL_TEMPERATURE:1", "E1 OilT", "deg F", lambda x: f"{ran_to_f(x):.2f}"),
    SimpleVar("ENG_OIL_PRESSURE:1", "E1 OilP", "psi", lambda x: f"{psf_to_psi(x):.2f}"),
    SimpleVar("RECIP_ENG_MANIFOLD_PRESSURE:1", "E1 MAP", "Hg", lambda x: f"{x:.2f}"),
    SimpleVar("GENERAL_ENG_RPM:1", "E1 RPM", "rpm", lambda x: f"{x:.1f}"),
    SimpleVar(
        "RECIP_ENG_CYLINDER_HEAD_TEMPERATURE:1",
        "E1 CHT1",
        "deg F",
        converter=lambda x: f"{c_to_f(x):.2f}",
    ),
    SimpleVar(
        "GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:1",
        "E1 EGT1",
        "deg F",
        lambda x: f"{ran_to_f(x):.2f}",
    ),
    SimpleVar("GPS_POSITION_ALT", "AltGPS", "ft wgs", lambda x: f"{x * 3.3:.1f}", 7),
    SimpleVar("AIRSPEED_TRUE", "TAS", "kt", lambda x: f"{int(x)}"),
    HsiSource("HSIS", "enum"),
    Course("CRS", "deg", 7),
    # TODO:  figure out why these all return the value for index 2
    # SimpleVar("NAV_ACTIVE_FREQUENCY:1", "NAV1", "MHz", lambda x: f"{x:.2f}", 6),
    # SimpleVar("NAV_ACTIVE_FREQUENCY:2", "NAV2", "MHz", lambda x: f"{x:.2f}", 6),
    # SimpleVar("COM_ACTIVE_FREQUENCY:1", "COM1", "MHz", lambda x: f"{x:.2f}", 6),
    # SimpleVar("COM_ACTIVE_FREQUENCY:2", "COM2", "MHz", lambda x: f"{x:.2f}", 6),
    SimpleVar("HSI_CDI_NEEDLE", "HCDI", "fsd", lambda x: f"{x / 127:.3f}", 6),
    SimpleVar("HSI_GSI_NEEDLE", "VCDI", "fsd", lambda x: f"{x / 127:.3f}", 6),
    SimpleVar("AMBIENT_WIND_VELOCITY", "WndSpd", "kt", lambda x: f"{x:.2f}"),
    SimpleVar("AMBIENT_WIND_DIRECTION", "WndDr", "deg", lambda x: f"{x:.1f}"),
    SimpleVar("GPS_WP_DISTANCE", "WptDst", "nm", lambda x: f"{m_to_nm(x):.1f}"),
    SimpleVar("GPS_WP_BEARING", "WptBRG", "deg", lambda x: f"{rad_to_deg(x):.1f}"),
    SimpleVar("GPS_MAGVAR", "MagVar", "deg", lambda x: f"{rad_to_deg(x):.1f}"),
    SimpleVar("AUTOPILOT_MASTER", "AfcsOn", "bool", lambda x: "1" if x else "0"),
    ApRollMode("RollM", "enum"),
    ApPitchMode("PitchM", "enum"),
    SimpleVar(
        "AUTOPILOT_FLIGHT_DIRECTOR_BANK",
        "RollC",
        "deg",
        lambda x: f"{rad_to_deg(x):.1f}",
    ),
    SimpleVar(
        "AUTOPILOT_FLIGHT_DIRECTOR_PITCH",
        "PtchC",
        "deg",
        lambda x: f"{rad_to_deg(x):.1f}",
    ),
]
