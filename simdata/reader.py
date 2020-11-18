import time

from .conversions import *

import msgpack
from SimConnect import *

class Reader:
    def __init__(self):
        self._sc = None
        self._aq = None
        self._proplist = self._known_properties

    def connect(self):
        self._sc = SimConnect()
        self._aq = AircraftRequests(self._sc, _time=0)

    @property
    def connected(self):
        if self._sc:
            return True
        return False

    @property
    def _known_properties(self):
        ignored_props = ("proplist", "connect", "connected", "withvar")
        return [x for x in dir(self) if (x not in ignored_props and x[0] != "_")]
    
    @property
    def proplist(self):
        return self._proplist

    @proplist.setter
    def proplist(self, proplist):
        badprops = [x for x in proplist if x not in self._known_properties]
        if len(badprops) == 0:
            self._proplist = proplist
        elif len(badprops) == 1:
            raise ValueError(f"Unknown property: {badprops[0]}")
        else:
            raise ValueError(f"Unknown properties: {' '.join(badprops)}")
        self._proplist = proplist

    def withvar(name, simvar):
        def wrapper(f):
            def wrapped_withvar(*args, **kwargs):
                if not args[0].connected:
                    raise ConnectionError("Not connected to flight simulator.")
                kwargs[name]=args[0]._aq.find(simvar)
                try:
                    return f(*args, **kwargs)
                except (TypeError, AttributeError) as exc:
                    print(f"EXCEPTION: {exc}")
                    return None
            return wrapped_withvar
        return wrapper


    @property
    @withvar('year', 'LOCAL_YEAR')
    @withvar('month', 'LOCAL_MONTH_OF_YEAR')
    @withvar('day', 'LOCAL_DAY_OF_MONTH')
    def local_date(self, year, month, day):
        year = int(year.value)
        month = int(month.value)
        day = int(day.value)
        return f"{year:4}-{month:02}-{day:02}"

    @property
    @withvar('ltime', 'LOCAL_TIME')
    def local_time(self, ltime):
        return time.strftime("%H:%M:%S", time.gmtime(ltime.value))

    @property
    @withvar('offset', 'TIME_ZONE_OFFSET')
    def utc_offset(self, offset):
        offset_secs = offset.value
        if offset_secs <= 0:
            prefix = "+"
            offset_secs *= -1
        else:
            prefix = "-"
        return f"{prefix}{time.strftime('%H:%M', time.gmtime(offset_secs))}"

    @property
    @withvar('wp', "GPS_WP_NEXT_ID")
    def next_wp(self, wp):
        return wp.value.decode("utf-8")

    @property
    @withvar('lat', "GPS_POSITION_LAT")
    def lat(self, lat):
        return lat.value

    @property
    @withvar('lon', 'GPS_POSITION_LON')
    def lon(self, lon):
        return lon.value

    @property
    @withvar('alt', 'INDICATED_ALTITUDE')
    def alt_indicated(self, alt):
        return alt.value

    @property
    @withvar('baro', 'KOHLSMAN_SETTING_HG')
    def baro(self, baro):
        return baro.value

    @property
    @withvar('alt', 'PLANE_ALTITUDE')
    def alt_msl(self, alt):
        return alt.value

    @property
    @withvar('oat', 'AMBIENT_TEMPERATURE')
    def oat(self, oat):
        return oat.value

    @property
    @withvar('ias', 'AIRSPEED_INDICATED')
    def ias(self, ias):
        return ias.value

    @property
    @withvar('gs', 'GROUND_VELOCITY')
    def gs(self, gs):
        return gs.value

    @property
    @withvar('vs', 'VERTICAL_SPEED')
    def vs(self, vs):
        return vs.value / 60 #fps to fpm

    @property
    @withvar('pitch', 'PLANE_PITCH_DEGREES')
    def pitch(self, pitch):
        # default is in rads with pitch up negative
        return rad_to_deg(pitch.value * -1)

    @property
    @withvar('roll', 'PLANE_BANK_DEGREES')
    def roll(self, roll):
        # default is in rads, and I like right roll positive
        return rad_to_deg(roll.value * -1)

    @property
    @withvar('latg', 'ACCELERATION_BODY_X')
    def latg(self, latg):
        return fps2_to_g(latg.value)

    @property
    @withvar('vertg', 'ACCELERATION_BODY_Y')
    def vertg(self, vertg):
        return fps2_to_g(vertg.value)
        
    @property
    @withvar('hdg', 'PLANE_HEADING_DEGREES_MAGNETIC')
    def hdg(self, hdg):
        return rad_to_deg(hdg.value)

    @property
    @withvar('trk', 'GPS_GROUND_MAGNETIC_TRACK')
    def trk(self, trk):
        return rad_to_deg(trk.value)

    @property
    @withvar('volts', 'ELECTRICAL_BATTERY_BUS_VOLTAGE')
    def volts(self, volts):
        return volts.value

    @property
    @withvar('qty', 'FUEL_LEFT_QUANTITY')
    def fuel_l(self, qty):
        return qty.value

    @property
    @withvar('qty', 'FUEL_RIGHT_QUANTITY')
    def fuel_r(self, qty):
        return qty.value

    # TODO:  center/alt quantities?

    @property
    @withvar('gph', 'ENG_FUEL_FLOW_GPH:1')
    def eng1_gph(self, gph):
        return gph.value

    @property
    @withvar('gph', 'ENG_FUEL_FLOW_GPH:2')
    def eng2_gph(self, gph):
        return gph.value

    @property
    @withvar('temp', 'ENG_OIL_TEMPERATURE:1')
    def eng1_oil_temp(self, temp):
        return ran_to_f(temp.value)

    @property
    @withvar('temp', 'ENG_OIL_TEMPERATURE:2')
    def eng2_oil_temp(self, temp):
        return ran_to_f(temp.value)

    @property
    @withvar('psf', 'ENG_OIL_PRESSURE:1')
    def eng1_oil_press(self, psf):
        return psf_to_psi(psf.value)

    @property
    @withvar('psf', 'ENG_OIL_PRESSURE:2')
    def eng2_oil_press(self, psf):
        return psf_to_psi(psf.value)

    @property
    @withvar('hg', 'RECIP_ENG_MANIFOLD_PRESSURE:1')
    def eng1_map(self, hg):
        return hg.value

    @property
    @withvar('hg', 'RECIP_ENG_MANIFOLD_PRESSURE:2')
    def eng2_map(self, hg):
        return hg.value

    @property
    @withvar('rpm', 'GENERAL_ENG_RPM:1')
    def eng1_rpm(self, rpm):
        return rpm.value

    @property
    @withvar('rpm', 'GENERAL_ENG_RPM:2')
    def eng2_rpm(self, rpm):
        return rpm.value

    @property
    @withvar('cht', 'RECIP_ENG_CYLINDER_HEAD_TEMPERATURE:1')
    def eng1_cht(self, cht):
        return c_to_f(cht.value)

    @property
    @withvar('cht', 'RECIP_ENG_CYLINDER_HEAD_TEMPERATURE:2')
    def eng2_cht(self, cht):
        return c_to_f(cht.value)

    @property
    @withvar('egt', 'GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:1')
    def eng1_egt(self, egt):
        return ran_to_f(egt.value)

    @property
    @withvar('egt', 'GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:2')
    def eng2_egt(self, egt):
        return ran_to_f(egt.value)

    @property
    @withvar('alt', 'GPS_POSITION_ALT')
    def alt_gps(self, alt):
        return alt.value * 3.3

    @property
    @withvar('tas', 'AIRSPEED_TRUE')
    def tas(self, tas):
        return tas.value

    @property
    @withvar('nav_select', 'AUTOPILOT_NAV_SELECTED')
    @withvar('gps_drives', 'GPS_DRIVES_NAV1')
    def hsi_source(self, nav_select, gps_drives):
        if gps_drives.value:
            return "GPS"
        else:
            return f"NAV{int(nav_select.value)}"

    @property
    @withvar('nav_select', 'AUTOPILOT_NAV_SELECTED')
    @withvar('gps_drives', 'GPS_DRIVES_NAV1')
    @withvar('dtk', 'GPS_WP_DESIRED_TRACK')
    @withvar('obs1', 'NAV_OBS:1')
    @withvar('obs2', 'NAV_OBS:2')
    def course(self, nav_select, gps_drives, dtk, obs1, obs2):
        if gps_drives.value:
            crs = rad_to_deg(dtk.value)
        elif nav_select.value == 1:
            crs = obs1.value
        else:
            crs = obs2.value
        return crs

    @property
    @withvar('nav', 'NAV_ACTIVE_FREQUENCY:1')
    def nav1(self, nav):
        return nav.value

    @property
    @withvar('nav', 'NAV_ACTIVE_FREQUENCY:2')
    def nav2(self, nav):
        return nav.value

    @property
    @withvar('com', 'COM_ACTIVE_FREQUENCY:1')
    def com1(self, com):
        return com.value

    @property
    @withvar('com', 'COM_ACTIVE_FREQUENCY:2')
    def com2(self, com):
        return com.value

    @property
    @withvar('cdi', 'HSI_CDI_NEEDLE')
    def hcdi(self, cdi):
        return cdi.value / 127

    @property
    @withvar('cdi', 'HSI_GSI_NEEDLE')
    def vcdi(self, cdi):
        return cdi.value / 127

    @property
    @withvar('spd', 'AMBIENT_WIND_VELOCITY')
    def wind_spd(self, spd):
        return spd.value

    @property
    @withvar('drct', 'AMBIENT_WIND_DIRECTION')
    def wind_dir(self, drct):
        return drct.value

    @property
    @withvar('dist', 'GPS_WP_DISTANCE')
    def wp_dist(self, dist):
        return m_to_nm(dist.value)

    @property
    @withvar('brg', 'GPS_WP_BEARING')
    def wp_brg(self, brg):
        return rad_to_deg(brg.value)

    @property
    @withvar('magvar', 'GPS_MAGVAR')
    def magvar(self, magvar):
        return rad_to_deg(magvar.value)

    @property
    @withvar('ap', 'AUTOPILOT_MASTER')
    def ap_master(self, ap):
        return ap.value

    @property
    def roll_mode(self):
        return None # TODO

    @property
    def pitch_mode(self):
        return None # TODO

    @property
    @withvar('bank', 'AUTOPILOT_FLIGHT_DIRECTOR_BANK')
    def ap_roll_cmd(self, bank):
        return rad_to_deg(bank.value)

    @property
    @withvar('pitch', 'AUTOPILOT_FLIGHT_DIRECTOR_PITCH')
    def ap_pitch_cmd(self, pitch):
        return rad_to_deg(pitch.value)


class Dumper:
    def __init__(self, reader=None):
        if not reader:
            reader = Reader()
        self._reader = reader
        self._reader.connect()

    def dumper(self, proplist, interval_secs = 1):
        if not self._reader.connected:
            raise ConnectionError("Not connected to flight simulator.")
        self._reader.proplist = proplist
        last_read = None
        while True:
            now = time.time()
            if not last_read or now - last_read >= interval_secs:
                last_read = now
                vals = {}
                for prop in proplist:
                    vals[prop] = self._reader.__getattribute__(prop)
                yield msgpack.packb(vals)
            else:
                time.sleep(0.1)