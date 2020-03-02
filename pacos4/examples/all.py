from .pingpong.serial import main as main_pinpong_serial
from .pingpong.parallel import main as main_pinpong_parallel
from .pingpong.parallel_slow_sim_hw import (
        main as main_pinpong_parallel_slow_sim_hw)
from .periodic import main as main_periodic
from .parallel_count import main as main_parallel_count
from .race.timer_race import main as main_timer_race
from .race.data_race import main as main_data_race
from .race.best_effort_race import main as main_best_effort_race
#from .race.data_race_tackon import main as main_data_race_tackon


if __name__ == "__main__":
    main_pinpong_serial()
    main_pinpong_parallel()
    main_pinpong_parallel_slow_sim_hw()
    main_parallel_count()
    main_timer_race()
    main_data_race()
    main_best_effort_race()
