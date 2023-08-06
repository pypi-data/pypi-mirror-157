import datetime as dt


LOCAL_TIMEZONE = dt.timezone(
    dt.timedelta(hours=8),
    name='Asia/Shanghai',
)


class CommonDateTimeFormats:
    """
    常用日期时间格式
    """
    s_dt = '%Y/%m/%d %H:%M:%S'
    ms_dt = "%Y/%m/%d %H:%M:%S.%f"

    s_int = "%Y%m%d%H%M%S"
    ms_int = "%Y%m%d%H%M%S%f"

    _date_and_time_ls = s_dt.split(' ')
    only_date = _date_and_time_ls[0]
    only_time = _date_and_time_ls[-1]


common_date_time_formats = CommonDateTimeFormats()


DEFAULT_TIME_FORMAT = common_date_time_formats.s_dt
DEFAULT_DECIMAL_PLACES = 2


def get_current_beijing_time_dt():
    utc_now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

    # 北京时间
    current_beijing_time_dt = utc_now.astimezone(LOCAL_TIMEZONE)
    return current_beijing_time_dt


def get_current_beijing_time_str(fmt: str = None, decimal_places: (int, None) = None):
    """
    得到当前的北京时间字符串
    :param fmt: 时间格式
    :param decimal_places: 保留几位小数
    :return: 当前的北京时间字符串
    """
    current_beijing_time_dt = get_current_beijing_time_dt()

    if fmt is None:
        fmt = DEFAULT_TIME_FORMAT
        if decimal_places is None:
            decimal_places = DEFAULT_DECIMAL_PLACES

    if decimal_places:
        value_range = [0, 6]
        assert value_range[0] <= decimal_places <= value_range[1], f"decimal_places必须在{value_range}之间!"

        # 若没有以%f结尾, 则自动添加上毫秒格式
        if not fmt.endswith("%f"):
            fmt += ".%f"

        _current_beijing_time_str = current_beijing_time_dt.strftime(fmt)
        current_beijing_time_str = _current_beijing_time_str[:-(value_range[1] - decimal_places)] if decimal_places != value_range[1] else _current_beijing_time_str
    else:
        current_beijing_time_str = current_beijing_time_dt.strftime(fmt)

    return current_beijing_time_str


if __name__ == '__main__':
    # ret = get_current_beijing_time_str()
    ret = get_current_beijing_time_str(common_date_time_formats.ms_int, 0)
    print(ret)
    1
