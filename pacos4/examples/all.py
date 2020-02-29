from .pingpong.serial import main as main_pinpong_serial
from .pingpong.parallel import main as main_pinpong_parallel
from .pingpong.parallel_slow_sim_hw import main \
        as main_pinpong_parallel_slow_sim_hw
from .parallel_count import main as main_parallel_count
from .timer_race import main as main_timer_race
from .data_race import main as main_data_race


if __name__ == "__main__":
    main_pinpong_serial()
    main_pinpong_parallel()
    main_pinpong_parallel_slow_sim_hw()
    main_parallel_count()
    main_timer_race()
    main_data_race()
