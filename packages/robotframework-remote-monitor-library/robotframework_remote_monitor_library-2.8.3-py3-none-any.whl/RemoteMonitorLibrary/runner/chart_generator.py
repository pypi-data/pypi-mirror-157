import os
import re

import pandas as pd
from matplotlib import pyplot as plt

from RemoteMonitorLibrary.model.chart_abstract import ChartAbstract
from RemoteMonitorLibrary.utils import get_error_info

#
# def _get_y_limit(data):
#     return max([max(y) for y in [x[1:] for x in data]])


def generate_charts(chart: ChartAbstract, sql_data, abs_image_path, prefix=None, **marks):
    try:
        errors = []
        for data in chart.generate_chart_data(sql_data):
            try:
                title, x, y, chart_data = data
                file_name = f"{title}_{prefix}" if prefix else title
                file_name = chart.file_name.format(name=file_name.lower())
                file_path = os.path.join(abs_image_path, re.sub(r'\s+|@|:', '_', file_name))
                if os.path.exists(file_path):
                    os.remove(file_path)
                plt.style.use('classic')
                df = pd.DataFrame(chart_data, columns=y, index=x)
                y_limit = chart.get_y_limit(chart_data)
                df.cumsum()
                mp = df.plot(legend=True)
                for label in mp.axes.get_xticklabels():
                    label.set_rotation(25)
                    label.set_x(10)
                plt.ylim(0, y_limit * 1.3)
                plt.xlabel('Time')
                plt.title(title)
                # TODO: Add vertical mark line on chart
                # if len(marks) > 0:
                #     fig, ax = plt.subplots()
                #     for mark, time in marks.items():
                #         ax.axvline(df.index.searchsorted(time),
                #         color='red', linestyle="--", lw=2, label="lancement")
                #     plt.tight_layout()
                plt.savefig(file_path)
                yield title.upper(), file_path
            except Exception as e:
                f, li = get_error_info()
                errors.append(f"{e}; File; {f}:{li}")
    except Exception as e:
        f, l = get_error_info()
        raise RuntimeError(f"Probably SQL query failed; Reason: {e}; File: {f}:{l}")
    else:
        if len(errors) > 0:
            raise RuntimeError("Following sub charts creation error:\n\t{}".format(
                '\n\t'.join([f"{i}. {e}" for i, e in enumerate(errors)])
            ))
