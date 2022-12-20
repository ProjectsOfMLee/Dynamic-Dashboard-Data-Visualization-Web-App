import pandas as pd
import json


def get_dataset(df, dropdown_value):
    ds = json.loads(df)

    if dropdown_value == "uniform_random":
        df_query = pd.read_json(ds['ur_df'], orient='split').copy()
    elif dropdown_value == "thompson_sampling_contextual":
        df_query = pd.read_json(ds['tsc_df'], orient='split').copy()
    else:
        df_query = pd.read_json(ds['df'], orient='split').copy()

    reward_var = ds['rv']

    return df_query, reward_var


def filter_by_time(df_query, timezone_change_type, timerange_change_type, time_slider=None):
    df_query['reward_create_time'] = pd.to_datetime(df_query['reward_create_time']).dt.tz_convert(timezone_change_type)
    df_query['arm_assign_time'] = pd.to_datetime(df_query['arm_assign_time']).dt.tz_convert(timezone_change_type)

    day_offset = 7 if timerange_change_type == "week" else 1

    last_reward_idx = df_query['reward_create_time'].last_valid_index()
    last_arm_idx = -1

    if last_reward_idx is not None and df_query['reward_create_time'].iloc[last_reward_idx] > df_query['arm_assign_time'].iloc[last_arm_idx]:
        time_range = pd.date_range(
            start=df_query['arm_assign_time'].iloc[0] -
            pd.offsets.Day(day_offset),
            end=df_query['reward_create_time'].iloc[last_reward_idx] +
            pd.offsets.Day(day_offset),
            tz=timezone_change_type,
            freq=f"{day_offset}D",
            inclusive="right"
        )
    else:
        time_range = pd.date_range(
            start=df_query['arm_assign_time'].iloc[0] -
            pd.offsets.Day(day_offset),
            end=df_query['arm_assign_time'].iloc[last_arm_idx] +
            pd.offsets.Day(day_offset),
            tz=timezone_change_type,
            freq=f"{day_offset}D",
            inclusive="right"
        )
    
    if time_slider:
        df_query = df_query.loc[
            (df_query['arm_assign_time'] >= str(time_range[max(0, time_slider[0])])) & \
            (df_query['arm_assign_time'] < str(time_range[min(time_slider[1], len(time_range) - 1)]))
        ]
    
    return df_query, time_range
