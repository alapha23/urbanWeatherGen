
import os
import pytest
import UWG
import math

class TestUWG(object):
    """Test for UWG.py
    Naming: Test prefixed test classes (without an __init__ method)
    for test autodetection by pytest
    """
    DIR_UP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DIR_EPW_PATH = os.path.join(DIR_UP_PATH,"resources/epw")

    def setup_init_uwg(self):
        epw_dir = self.DIR_EPW_PATH
        epw_file_name = "SGP_Singapore.486980_IWEC.epw"
        uwg_param_dir = os.path.join(self.DIR_UP_PATH,"resources")
        uwg_param_file_name = "initialize.uwg"

        self.uwg = UWG.UWG(epw_dir, epw_file_name, uwg_param_dir, uwg_param_file_name)

    def test_read_epw(self):
        self.setup_init_uwg()
        self.uwg.read_epw()

        # test header
        assert self.uwg._header[0][0] == "LOCATION"
        assert self.uwg._header[0][1] == "SINGAPORE"
        assert self.uwg.lat == pytest.approx(1.37, abs=1e-3)
        assert self.uwg.lon == pytest.approx(103.98, abs=1e-3)
        assert self.uwg.GMT == pytest.approx(8, abs=1e-3)
        # test soil data
        assert self.uwg.nSoil == pytest.approx(3, abs=1e-2)
        # test soil depths
        assert self.uwg.depth_soil[0][0] == pytest.approx(0.5, abs=1e-3)
        assert self.uwg.depth_soil[1][0] == pytest.approx(2., abs=1e-3)
        assert self.uwg.depth_soil[2][0] == pytest.approx(4., abs=1e-3)
        # test soil temps over 12 months
        assert self.uwg.Tsoil[0][0] == pytest.approx(27.55+273.15, abs=1e-3)
        assert self.uwg.Tsoil[1][2] == pytest.approx(28.01+273.15, abs=1e-3)
        assert self.uwg.Tsoil[2][11] == pytest.approx(27.07+273.15, abs=1e-3)
        # test time step in weather file
        assert self.uwg.epwinput[0][0] == "1989"
        assert float(self.uwg.epwinput[3][6]) == pytest.approx(24.1,abs=1e-3)

    def test_read_input(self):
        self.setup_init_uwg()
        self.uwg.read_epw()
        self.uwg.read_input()
        self.uwg.set_input()

        #test uwg param dictionary first and last
        assert self.uwg._init_param_dict.has_key('bldHeight') == True
        assert self.uwg._init_param_dict.has_key('h_obs') == True
        #test values
        assert self.uwg._init_param_dict['bldHeight'] == pytest.approx(10., abs=1e-6)
        assert self.uwg._init_param_dict['vegEnd'] == pytest.approx(10, abs=1e-6)
        assert self.uwg._init_param_dict['albRoof'] == pytest.approx(0.5, abs=1e-6)
        assert self.uwg._init_param_dict['h_ubl1'] == pytest.approx(1000., abs=1e-6)
        assert self.uwg._init_param_dict['h_ref'] == pytest.approx(150., abs=1e-6)

        # test SchTraffic schedule
        assert self.uwg._init_param_dict['SchTraffic'][0][0] == pytest.approx(0.2, abs=1e-6) # first
        assert self.uwg._init_param_dict['SchTraffic'][2][23] == pytest.approx(0.2, abs=1e-6) # last
        assert self.uwg._init_param_dict['SchTraffic'][0][19] == pytest.approx(0.8, abs=1e-6)
        assert self.uwg._init_param_dict['SchTraffic'][1][21] == pytest.approx(0.3, abs=1e-6)
        assert self.uwg._init_param_dict['SchTraffic'][2][6] == pytest.approx(0.4, abs=1e-6)

        # test bld fraction list
        assert self.uwg._init_param_dict['bld'][0][0] == pytest.approx(0., abs=1e-6)
        assert self.uwg._init_param_dict['bld'][3][1] == pytest.approx(0.4, abs=1e-6)
        assert self.uwg._init_param_dict['bld'][5][1] == pytest.approx(0.6, abs=1e-6)
        assert self.uwg._init_param_dict['bld'][15][2] == pytest.approx(0.0, abs=1e-6)

        # test BEMs
        assert len(self.uwg.BEM) == pytest.approx(2.,abs=1e-6)
        # test BEM office (BLD4 in DOE)
        assert self.uwg.BEM[0].building.Type == "LargeOffice"
        assert self.uwg.BEM[0].building.Zone == "1A (Miami)"
        assert self.uwg.BEM[0].building.Era == "Pst80"
        assert self.uwg.BEM[0].frac == 0.4

        # test BEM apartment
        assert self.uwg.BEM[1].building.Type == "MidRiseApartment"
        assert self.uwg.BEM[1].building.Zone == "1A (Miami)"
        assert self.uwg.BEM[1].building.Era == "Pst80"
        assert self.uwg.BEM[1].frac == 0.6

        # Check that schedules are called correctly
        assert self.uwg.Sch[0].Light[0][8] == pytest.approx(0.9, abs=1e-6)   #9am on Weekday for Office
        assert self.uwg.Sch[0].Light[0][7] == pytest.approx(0.3, abs=1e-6)   #9am on Weekday for Office
        assert self.uwg.Sch[1].Occ[1][11] == pytest.approx(0.25, abs=1e-6)     #12 noon on Weekend for apt

        # Check that soil ground depth is set correctly
        assert self.uwg.depth_soil[self.uwg.soilindex1][0] == pytest.approx(0.5, abs=1e-6)
        assert self.uwg.depth_soil[self.uwg.soilindex2][0] == pytest.approx(0.5, abs=1e-6)

        #self.road
        # Check the road layer splitting
        assert len(self.uwg.road.layerThickness) == pytest.approx(11., abs=1e-15)
        assert self.uwg.road.layerThickness[0] == pytest.approx(0.05, abs=1e-15)

        # Check the road layer splitting for rural
        assert len(self.uwg.rural.layerThickness) == pytest.approx(11., abs=1e-15)
        assert self.uwg.rural.layerThickness[0] == pytest.approx(0.05, abs=1e-6)

    def test_procMat(self):
        """
        Test different max/min layer depths that generate different diffrent road layer
        thicknesses (to account for too deep elements with inaccurate heat transfer).
        """

        self.setup_init_uwg()
        self.uwg.read_epw()
        self.uwg.read_input()
        self.uwg.set_input()

        #test a 0.5m road split into 10 slices of 0.05m
        # base case; min=0.01, max=0.05, stays the same
        roadMat, newthickness = UWG.procMat(self.uwg.road, 0.05, 0.01)
        assert len(roadMat) == pytest.approx(11, abs=1e-6)
        assert len(newthickness) == pytest.approx(11, abs=1e-6)
        assert sum(newthickness) == pytest.approx(0.05*11, abs=1e-6)

        #TODO: revise
        # min=0.01, max=0.04, 0.05 cut into two = 0.025
        #roadMat, newthickness = UWG.procMat(self.uwg.road, 0.04, 0.01)
        #assert len(roadMat) == pytest.approx(20, abs=1e-6)
        #assert len(newthickness) == pytest.approx(20, abs=1e-6)
        #assert sum(newthickness) == pytest.approx(0.025*20, abs=1e-6)

        # min=0.06, max=0.1, should make new material at 0.06 thickness
        roadMat, newthickness = UWG.procMat(self.uwg.road, 0.1, 0.06)
        assert len(roadMat) == pytest.approx(11, abs=1e-6)
        assert len(newthickness) == pytest.approx(11, abs=1e-6)
        assert sum(newthickness) == pytest.approx(0.06*11, abs=1e-6)

        #TODO: revise
        # min=0.0001, max=0.1, should stay the same
        #roadMat, newthickness = UWG.procMat(self.uwg.road,0.1,0.0001)
        #assert len(roadMat) == pytest.approx(11, abs=1e-6)
        #assert len(newthickness) == pytest.approx(11, abs=1e-6)
        #assert sum(newthickness) == pytest.approx(0.5, abs=1e-6)

        # modify to one layer for tests
        self.uwg.road.layerThickness = [0.05]
        self.uwg.road.layerThermalCond = self.uwg.road.layerThermalCond[:1]
        self.uwg.road.layerVolHeat = self.uwg.road.layerVolHeat[:1]

        #0.05 layer, will split in two
        roadMat, newthickness = UWG.procMat(self.uwg.road, 0.05, 0.01)
        assert len(roadMat) == pytest.approx(2, abs=1e-6)
        assert len(newthickness) == pytest.approx(2, abs=1e-6)
        assert sum(newthickness) == pytest.approx(0.025*2, abs=1e-6)

        #0.015 layer, will split in min thickness in two
        self.uwg.road.layerThickness = [0.015]
        roadMat, newthickness = UWG.procMat(self.uwg.road, 0.05, 0.01)
        assert len(roadMat) == pytest.approx(2, abs=1e-6)
        assert len(newthickness) == pytest.approx(2, abs=1e-6)
        assert sum(newthickness) == pytest.approx(0.005*2, abs=1e-6)

        #0.12 layer, will split into 3 layers b/c > max_thickness
        self.uwg.road.layerThickness = [0.12]
        roadMat, newthickness = UWG.procMat(self.uwg.road, 0.05, 0.01)
        assert len(roadMat) == pytest.approx(3, abs=1e-6)
        assert len(newthickness) == pytest.approx(3, abs=1e-6)
        assert sum(newthickness) == pytest.approx(0.04*3, abs=1e-6)

    def test_hvac_autosize(self):

        self.setup_init_uwg()
        self.uwg.read_epw()
        self.uwg.read_input()
        self.uwg.set_input()
        self.uwg.hvac_autosize()

        assert self.uwg.BEM[0].building.coolCap == pytest.approx(9999., abs=1e-6)
        assert self.uwg.BEM[0].building.heatCap == pytest.approx(9999., abs=1e-6)
        assert self.uwg.BEM[1].building.coolCap == pytest.approx(9999., abs=1e-6)
        assert self.uwg.BEM[1].building.heatCap == pytest.approx(9999., abs=1e-6)
        assert len(self.uwg.BEM) == pytest.approx(2, abs=1e-6)

    def test_uwg_main(self):
        self.setup_init_uwg()
        self.uwg.read_epw()
        self.uwg.read_input()
        self.uwg.set_input()
        self.uwg.hvac_autosize()
        self.uwg.uwg_main()

        # Parameters from initialize.uwg
        # Month = 1;              % starting month (1-12)
        # Day = 1;                % starting day (1-31)
        # nDay = 31;              % number of days
        # dtSim = 300;            % simulation time step (s)
        # dtWeather = 3600;       % weather time step (s)

        assert self.uwg.N == pytest.approx(744., abs=1e-6)       # total hours in simulation
        assert self.uwg.ph == pytest.approx(0.083333, abs=1e-6)  # dt (simulation time step) in hours

        #test the weather data time series is equal to time step
        assert len(self.uwg.forcIP.infra) == pytest.approx((self.uwg.simTime.nt-1)/12., abs=1e-3)
        # check that simulation time is happening every 5 minutes 8928
        assert self.uwg.simTime.nt-1 == pytest.approx(31*24*3600/300., abs=1e-3)
        # check that weather step time is happening every 1 hour = 744
        assert len(self.uwg.forcIP.dif) ==  pytest.approx(31 * 24, abs=1e-3)

        # check that final day of timestep is at correct dayType
        assert self.uwg.dayType == pytest.approx(1., abs=1e-3)
        assert self.uwg.SchTraffic[self.uwg.dayType-1][self.uwg.simTime.hourDay] == pytest.approx(0.2, abs=1e-6)

    def test_uwg_output(self):
        self.setup_init_uwg()
        self.uwg.read_epw()
        self.uwg.read_input()

        # Test all year
        self.uwg.Month = 1
        self.uwg.Day = 1
        self.uwg.nDay = 1 # 365

        self.uwg.set_input()
        self.uwg.hvac_autosize()
        self.uwg.uwg_main()

        # shorten some variable names
        ti = self.uwg.simTime.timeInitial
        tf = self.uwg.simTime.timeFinal
        matlab_fname = "SGP_Singapore.486980_IWEC_UWG_Matlab.epw"

        # Get matlab data
        matlab_path_name = os.path.join(self.DIR_UP_PATH,"tests","matlab_ref","matlab_uwg",matlab_fname)

        # Get Matlab EPW file
        if not os.path.exists(matlab_path_name):
            raise Exception("Param file: '{}' does not exist.".format(matlab_path_name))

        # Open .uwg file and feed csv data to initializeDataFile
        try:
            new_epw = UWG.utilities.read_csv(matlab_path_name)
        except Exception as e:
            raise Exception("Failed to read .uwg file! {}".format(e.message))

        matlab_weather = UWG.weather.Weather(matlab_path_name,ti,tf)

        # Make weather files for testing
        python_weather = UWG.weather.Weather(self.uwg.newPathName,ti,tf)
        matlab_weather = UWG.weather.Weather(matlab_path_name, ti, tf)
        print '\n'

        assert len(python_weather.staTemp) == pytest.approx(len(matlab_weather.staTemp), abs=1e-15)

        # compare per hours
        for i in xrange(len(python_weather.staTemp)):
            print python_weather.staTemp[i], matlab_weather.staTemp[i] # dry bulb temperature  [?C]
            print python_weather.staTdp[i], matlab_weather.staTdp[i]   # dew point temperature [?C]
            print python_weather.staRhum[i], matlab_weather.staRhum[i] # relative humidity     [%]
            print python_weather.staUmod[i], matlab_weather.staUmod[i] # wind speed [m/s]
            print '---'


if __name__ == "__main__":
    test = TestUWG()
    #test.test_read_epw()
    #test.test_read_input()
    #test.test_procMat()
    #test.test_hvac_autosize()
    #test.test_uwg_main()
    test.test_uwg_output()
