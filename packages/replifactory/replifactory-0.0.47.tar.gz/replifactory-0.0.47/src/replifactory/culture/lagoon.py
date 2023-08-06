from replifactory.culture.culture_functions import dilute_adjust_drug1
from replifactory.culture.turbidostat import TurbidostatCulture
from replifactory.culture.chemostat import ChemostatCulture
from replifactory.culture.blank import BlankCulture
from replifactory.device.dilution import log_dilution
import time
import numpy as np


class LagoonCulture(BlankCulture):
    def __init__(self, directory: str = None, vial_number: int = None, name: str = "Species 1",
                 description: str = "Strain 1"):
        self.delay_feed_mins = 120
        self.dilution_factor_before_feed = 0.2
        self.feed_volume = 5
        self.max_dilution_volume = 10
        self.post_feed_pumped_air_volume = 5
        self.feed_vial_number = 1
        self.feed_min_od = 0.3

        # Running parameters
        super().__init__(directory=directory, vial_number=vial_number, name=name, description=description)

    def description_text(self):
        min_dilution_factor_single_dil = self.dead_volume/(self.max_dilution_volume + self.dead_volume)
        min_n_dilutions = np.ceil(np.log(self.dilution_factor_before_feed) / np.log(min_dilution_factor_single_dil))
        dilution_factor = self.dilution_factor_before_feed**(1/min_n_dilutions)
        pumped_volume = self.dead_volume/dilution_factor-self.dead_volume
        medium_use_per_day = min_n_dilutions*pumped_volume*(24*60/self.delay_feed_mins)+self.feed_volume

        t = f"""Every {self.delay_feed_mins:.0f} mins the {self.dead_volume:.1f}mL phage culture is diluted by a factor of {self.dilution_factor_before_feed:.2f}
then fed with {self.feed_volume:.2f}mL of bacterial culture from vial 1.
First feed: when vial{self.feed_vial_number:.0f} OD>{self.feed_min_od:.2f}
{min_n_dilutions} dilutions of {pumped_volume:.4f} mL ({min_n_dilutions*pumped_volume:.3f} mL total)
{medium_use_per_day:.2f}mL of medium per day
"""
        return t

    def feed_phage_to_od(self, od_target):
        if self.device.valves.not_all_closed():
            self.device.valves.close_all()

        self.device.valves.open(1)
        self.device.valves.open(2)

        od_feed = self.device.cultures[1].od
        est_vol = (od_target-self.od)*self.dead_volume/od_feed
        est_rotations = est_vol/5
        est_rot_per_sec = est_rotations / 6  # aim for about 6 seconds of pumping

        self.device.pump2.move(n_rotations=est_rotations, speed=est_rot_per_sec)
        for i in range(10):
            self.device.od_sensors[self.vial_number].measure_od()

    def test(self):
        assert type(self.device.cultures[1]) in [TurbidostatCulture, ChemostatCulture]

    def feed_phage(self, feed_volume=None):
        assert self.device.locks_vials[self.vial_number].acquire(timeout=60)
        assert self.device.locks_vials[self.feed_vial_number].acquire(timeout=60)
        assert self.device.lock_pumps.acquire(timeout=60)
        try:
            if feed_volume is None:
                feed_volume = self.feed_volume
            if self.device.valves.not_all_closed():
                self.device.valves.close_all()

            # # Fill feed vial
            self.device.stirrers.set_speed(1, 2)
            self.device.stirrers.set_speed(self.vial_number, 2)
            self.device.valves.open(1)
            self._last_dilution_start_time = time.time()
            self.device.pump1.pump(feed_volume)
            while self.device.pump1.is_pumping():
                time.sleep(0.5)
            log_dilution(device=self.device, vial_number=self.feed_vial_number, pump1_volume=feed_volume)

            # Transfer from feed
            self.device.valves.open(self.vial_number)
            self.device.stirrers.set_speed(1, 0)
            v1 = feed_volume + self.post_feed_pumped_air_volume
            self.device.pump1.pump(10, rot_per_sec=0.3)
            self.device.pump4.pump(10, rot_per_sec=0.5)
            self.device.pump2.pump(v1)
            while self.device.pump2.is_pumping():
                time.sleep(0.5)
            self.device.pump2.stop()
            self.device.pump1.stop()
            log_dilution(device=self.device, vial_number=self.vial_number, pump2_volume=feed_volume)

            # Remove excess
            excess_volume = feed_volume + 5
            self.device.valves.close(1)
            self.device.stirrers.set_speed(1, 2)
            self.device.pump4.stop()
            while self.device.pump4.is_pumping():
                time.sleep(0.2)
            self.device.pump4.reset()
            self.device.pump4.pump(excess_volume)
            stirrer_stopped = False
            while self.device.pump4.is_pumping():
                time.sleep(0.5)
                if self.device.pump4.get_pumped_volume() > feed_volume and not stirrer_stopped:
                    self.device.stirrers.set_speed(self.vial_number, 0)
                    stirrer_stopped = True
            self.device.stirrers.set_speed(self.vial_number, 2)
            self.device.valves.close(self.vial_number)
            log_dilution(device=self.device, vial_number=self.vial_number, pump4_volume=excess_volume)

        finally:
            if self.device.is_pumping():
                self.device.stop_pumps()
            self.device.locks_vials[self.vial_number].release()
            self.device.locks_vials[self.feed_vial_number].release()
            self.device.lock_pumps.release()

    def lower_od_phage(self, factor=None):
        """
        dilute culture with clean medium, multiple times if necessary to achieve the dilution factor
        :param factor: e.g 0.5 for a 1:2 dilution
        :return:
        """
        if factor is None:
            factor = self.dilution_factor_before_feed
        self._last_dilution_start_time = time.time()
        min_dilution_factor_single_dil = self.dead_volume/(self.max_dilution_volume + self.dead_volume)
        min_n_dilutions = int(np.ceil(np.log(self.dilution_factor_before_feed) / np.log(min_dilution_factor_single_dil)))
        dilution_factor = factor**(1/min_n_dilutions)
        pumped_volume = self.dead_volume/dilution_factor-self.dead_volume

        # print(f"min_dilution_factor_single_dil:{min_dilution_factor_single_dil},min_n_dilutions:{min_n_dilutions},dilution_factor:{dilution_factor},pumped_volume:{pumped_volume}")
        # print(f"{min_n_dilutions} dilutions of {pumped_volume:.4f} mL ({min_n_dilutions*pumped_volume:.3f} mL total)")
        for d in range(min_n_dilutions):
            self.dilute(pump1_volume=pumped_volume)

    def update(self, verbose=False):
        if self.is_active():
            self.update_growth_rate()
            if verbose:
                print("updated growth rate")

            if self._last_dilution_start_time is None:
                if verbose:
                    print("_last_dilution_start_time is None")
                feed = self.device.cultures[self.feed_vial_number]
                if feed.od > self.feed_min_od:
                    self.feed_phage()  # initial dilution
                else:
                    if verbose:
                        print("feed OD too low: %.2f" % feed.od)

            else:
                time_passed = time.time() - self._last_dilution_start_time
                delay_needed = self.delay_feed_mins * 60 - 55
                if time_passed >= delay_needed:
                    self.lower_od_phage()
                    self.feed_phage()
                else:
                    if verbose:
                        print("Not feeding yet, %d seconds to go" % (delay_needed - time_passed))
