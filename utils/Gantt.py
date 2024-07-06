import plotly.express as px
import pandas as pd


def plot_gantt_chart(machine_operations, savepath):
    data = []
    start_date = pd.Timestamp(0)
    for machine, operations in machine_operations.items():
        for op in operations:
            job, process, start_time, end_time = op
            data.append({
                'Machine': f'Machine {machine + 1}',  # 使用更具描述性的标签
                'Job': f'Job {job + 1}',  # 使用更具描述性的标签
                'Process': process,
                'Start': start_date + pd.Timedelta(milliseconds=start_time),
                'Finish': start_date + pd.Timedelta(milliseconds=end_time)
            })
    df = pd.DataFrame(data)

    fig = px.timeline(
        df,
        x_start='Start',
        x_end='Finish',
        y='Machine',
        color='Job',
        title=f'Gantt chart',
        category_orders={'Machine': [f'Machine {i}' for i in range(1, 50)]},  # 设置机器的顺序
    )

    fig.update_xaxes(
        tickformat="%Q",
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(values=["2024-12-25", "2025-01-01"])
        ]
    )
    fig.update_layout(yaxis=dict(tickmode='linear', tick0=1, dtick=1))
    fig.write_html(savepath)
