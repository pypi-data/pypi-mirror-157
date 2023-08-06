from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

import psycopg2
import psycopg2.extras

from ..model.config4features import temperature_labels


def _create_where(equality_constraints, interval_constraints):
    res = []
    for name in equality_constraints:
        values = equality_constraints[name]
        tmp = [(name, value) for value in values]
        ans = ' or '.join([f"{name}='{value}'" if value else f"{name} is NULL" for name, value in tmp])
        res.append(f"({ans})")

    equality_constraints = ' and '.join(res)

    res = []
    for name in interval_constraints:
        values = interval_constraints[name]
        tmp = [(name, value1, value2) for value1, value2 in values]
        # print(tmp)
        ans = ' or '.join([f"{name} between {value1} and {value2}" if value1 and value2 else
                            f"{name} >= {value1}" if value1 else
                            f"{name} <= {value2}" for name, value1, value2 in tmp])
        res.append(f"({ans})")

    interval_constraints = ' and '.join(res)

    if equality_constraints or interval_constraints:
        if equality_constraints and interval_constraints:
            return f"{equality_constraints} and {interval_constraints}"
        else:
            if equality_constraints:
                return f"{equality_constraints}"
            else:
                return f"{interval_constraints}"
    else:
        return ""


class LocalDB_Connector:
    def __init__(self,
                 server: str = '', user: str = '', password: str = '', db: str = ''):
        self.conn = psycopg2.connect(database=db,
                                     host=server,
                                     user=user,
                                     password=password)
        self.cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        self.user = user

        self.engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{server}/{db}')


    def close(self):
        try:
            self.conn.close()
        except Exception as exc:
            pass
        return


    def datetme2str(self, value):
        # str representation has to be compatible with sql server
        # yyyy-mm-dd
        return value.strftime('%Y-%m-%d %H:%M:%S')

    def select_single(self, query, column):
        self.cursor.execute(query)
        targets = [row[column] for row in self.cursor.fetchall()]
        if targets:
            return targets[0]
        else:
            return None

    def get_target_id(self, target: str):
        return int(self.select_single(f"select target_id from Targets where name=\'{target}\'", 'target_id'))

    def get_model_id(self, status: int):
        return self.select_single(f"select model_id from Models where status={status}", 'model_id')

    def get_status(self, model_id: int):
        return self.select_single(f"select status from Models where model_id={model_id}", 'status')

    def get_startdate(self, model_id: int):
        return self.select_single(f"select start from Models where model_id={model_id}", 'start')

    def get_enddate(self, model_id: int):
        return self.select_single(f"select \"end\" from Models where model_id={model_id}", 'end')

    def get_model_parameters(self, model_id: int):
        self.cursor.execute(f"select algorithm, grouping, autofeat from Models where model_id={model_id}")
        args = [(row['algorithm'], row['grouping'], row['autofeat']) for row in self.cursor.fetchall()]
        return args[0]

    def get_models_info(self):
        self.cursor.execute("select model_id, \"end\", status from Models order by status")
        return self.cursor.fetchall()


    def get_targets(self, model_id:int):
        model_id = (model_id, )

        query = """select name
                        from TargetsToModel as T1
                        inner join Targets as T2
                        on T1.target_id = T2.target_id
                        where T1.model_id=%s"""
        self.cursor.execute(query, (model_id,))
        targets = [row['name'] for row in self.cursor.fetchall()]
        return targets

    def get_features(self, model_id: int):
        model_id = (model_id, )
        query = """select name
                        from ColumnsToModels as T1
                        inner join Columns as T2
                        on T1.column_id = T2.column_id
                        where T1.model_id=%s
                        and T2.type=False"""
        self.cursor.execute(query, (model_id,))

        feature_columns = [row['name'] for row in self.cursor.fetchall()]
        return feature_columns


    def update_status(self, model_id: int, status: int = 1):
        query = '''update Models set status = %s
                   where model_id = %s'''
        self.cursor.execute(query, (status, model_id))
        self.conn.commit()
        return

    def update_end(self, model_id, end):
        end = self.datetme2str(end)
        query = '''update Models set \"end\"=%s
                    where model_id=%s'''
        self.cursor.execute(query, (end, int(model_id)))
        self.conn.commit()
        return


    def insert_metrics(self, model_id, target, r2, std, delta, relative_error, num_samples):
        target_id = self.get_target_id(target)
        self.cursor.execute("select * from Metrics")
        metrics2ids = {row['name']:row['metric_id'] for row in self.cursor.fetchall()}
        now_time = datetime.now()
        query = '''insert into
                    MetricToModels(model_id, target_id,
                    metric_id, value, time)
                    values (%s, %s, %s, %s, %s)'''

        performance_dict = {'R2': r2, 'std': std, 'delta': delta,
                            'relative_error': relative_error, 'Samples': num_samples}

        for metric_name in performance_dict:
            self.cursor.execute(query, (model_id, target_id,
                                        metrics2ids[metric_name],
                                        performance_dict[metric_name],
                                        now_time))
            self.conn.commit()


    def remove_target_specific_constraints(self, constraints, remove_target_specific):
        if remove_target_specific:
            for tl in temperature_labels:
                constraints.pop(tl, None)
        return constraints

    def get_equality_constraint(self, model_id: int, remove_target_specific=False):
        query = """select name, value from Filters_cat as a1
                   inner join Columns as a2
                   on a1.column_id=a2.column_id
                   where model_id = %s """

        self.cursor.execute(query, (model_id,))
        df = pd.DataFrame(self.cursor.fetchall())

        if df.empty:
            return {}
        else:
            filters = df.groupby('name')['value'].apply(lambda x: x.values.tolist()
                                                       ).to_dict()
            return self.remove_target_specific_constraints(filters, remove_target_specific)

    def get_interval_constraint(self, model_id: int, remove_target_specific=False):
        query = """select name, "begin", "end" from Filters_num as a1
                   inner join Columns as a2
                   on a1.column_id=a2.column_id
                   where model_id = %s """

        self.cursor.execute(query, (model_id,))

        df = pd.DataFrame(self.cursor.fetchall())
        if df.empty:
            return {}
        else:
            filters = df.groupby('name')[['begin', 'end']].apply(lambda x: x.values.tolist()
                                                                ).to_dict()
            return self.remove_target_specific_constraints(filters, remove_target_specific)


    def get_last_processed_date(self):
        # format : yyyy-mm-dd
        date = self.select_single(f"select last_processed_date from systeminfo where id=1", 'last_processed_date')
        last_three_days = datetime.now()-timedelta(3)
        if last_three_days > date:
            return last_three_days
        else:
            return date

    def set_last_processed_date(self, datetime):
        # format : yyyy-mm-dd
        date = self.datetme2str(datetime)
        query = '''update systeminfo set last_processed_date=%s
                    where id=1'''
        self.cursor.execute(query, (date,))
        self.conn.commit()
        return


    def save_predictions(self, df_pred, model_id, target_id):
        df_pred["model_id"] = model_id
        df_pred["target_id"] = target_id

        df_pred.to_sql('predictions', self.engine, if_exists='append', index=False)

    # deprecated: data not saved in local db now
    def get_filtered_data(self, model_id, start_date):
        start = self.datetme2str(start)

        eq_constr = self.get_equality_constraint(model_id)
        in_constr = self.get_interval_constraint(model_id)
        filters = _create_where(eq_constr, in_constr)
        query = f"select * from Data where НАЧ_ПРОКАТ>='{start}'"
        if filters:
            query += " and " + filters

        df = pd.read_sql_query(query, self.conn)
        return df
