import plotly.express as px
import pandas as pd
import plotly.io as pio

def common_setting(fig):
    fig.update_xaxes(tickformat="%y/%m/%d")
    fig.update_layout(
        # サイズ調整
        autosize=True,

        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',

        margin=dict(l=0,r=10,t=0,b=30),

        title_font=dict(size=14),            # タイトル文字サイズ
        font=dict(size=8),                  # 軸ラベル・凡例などの共通サイズ

        legend=dict(
            visible=True,
            orientation="h",
            yanchor="top",
            y=1.2,
            xanchor="right",
            x=1,
        )
    )

    return fig

def display_total_assets(df):
    fig = px.line(
        df, x=df.index, y=["資産額_実績", "資産額_目標"],template="plotly_dark",
            labels={"date": "日付", "value":"資産額","variable":""}
        )
    fig = common_setting(fig)
    return fig

def display_total_returns(df):
    fig = px.line(df, x=df.index, y=["トータルリターン_実績", "トータルリターン_目標"],
            labels={"date": "日付", "value":"リターン額","variable":""}, template="plotly_dark")
    fig = common_setting(fig)
    return fig

def display_general_income_expenditure(df):
    fig = px.bar(
        df, x=df.index, y=["金額_収入", "金額_支出"],barmode='group', template='plotly_dark',
            labels={'value':'金額', 'date':'年月', 'variable':''})
    #fig.show()
    fig.add_scatter(
        x=df.index,
        y=df['目標_収入'],
        mode='lines+markers',
        name='目標_収入',
        line=dict(color='blue', width=2)
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_支出'],
        mode='lines+markers',
        name='目標_支出',
        line=dict(color='orange', width=2)
    )
    fig = common_setting(fig)
    return fig

def display_general_balance(df):
    # 4. 一般収支
    fig = px.bar(
        df, x=df.index, y=["金額_収支"], template='plotly_dark',
            labels={'value':'金額', 'date':'年月', 'variable':''},
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_収支'],
        mode='lines+markers',
        name='目標_収支',
        line=dict(color='orange', width=2)
    )
    fig = common_setting(fig)
    return fig

def display_special_income_expenditure(df):
    fig = px.bar(
        df, x=df.index, y=["金額_収入", "金額_支出"],barmode='group', template='plotly_dark',
            labels={'value':'金額', 'date':'年月', 'variable':''})

    fig.add_scatter(
        x=df.index,
        y=df['目標_収入'],
        mode='lines+markers',
        name='目標_収入',
        line=dict(color='blue', width=2)
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_支出'],
        mode='lines+markers',
        name='目標_支出',
        line=dict(color='orange', width=2)
    )
    fig = common_setting(fig)
    return fig

def display_special_balance(df):
    fig = px.line(
        df, x=df.index, y=["金額_収支","目標_収支"], template='plotly_dark', markers=True,
            labels={'value':'金額', 'date':'年月', 'variable':''}
    )
    fig = common_setting(fig)
    return fig

def write_html(fig, id: str):
    fig_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs='cdn',
        config = {"responsive": True},
        div_id = id
    )
    return fig_html