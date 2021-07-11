import os
import pandas as pd
import win32com.client as win32
from datetime import datetime


class PathBuilder(object):
    def __init__(self, folder, file) -> None:
        self.folder = folder
        self.file = file

    def build(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(current_path, self.folder, self.file)

        return file_name


class ExcelPivotTable(object):
    def __init__(self, file, sheet, excel_range):
        self.sheet = sheet
        self.excel_range = excel_range
        self.file_path = PathBuilder(folder='input_files', file=file).build()

    def open(self):
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True

        workbook = excel.Workbooks.Open(self.file_path)
        worksheet = workbook.Sheets(self.sheet)

        pivot = worksheet.Range(self.excel_range).PivotTable

        return pivot


class ExtractDataFromPivot(object):
    def __init__(self, uf_filter, product_filter, file, sheet, excel_range) -> None:
       self.uf_filter = uf_filter
       self.product_filter = product_filter
       self.created_time = datetime.now()
       self._pivot = ExcelPivotTable(
           file=file,
           sheet=sheet,
           excel_range=excel_range
        ).open()

    def filter_pivot(self, pivot, filter:str, value:str) -> None:
        pivot.PivotFields(filter).CurrentPage = value.Name

    def build_dataframe(self, uf:str, product:str, unit:str) -> pd.DataFrame:
        month_row = {}
        year_column = {}
        value_row_column = {}
        for item in self._pivot.TableRange1:

            if item.Row == self._pivot.TableRange1.Row:
                continue
            
            # Year column based dictionary
            if item.Row == self._pivot.TableRange1.Row + 1 \
            and item.Column > self._pivot.TableRange1.Column :
                year_column[item.Column] = int(item.Value)

            # Month row based dictonary
            if item.Row > self._pivot.TableRange1.Row + 1 \
            and item.Column == self._pivot.TableRange1.Column:
                month_row[item.Row] = item.Value

            # Values row and column based dictionary
            if item.Row > self._pivot.TableRange1.Row + 1 \
            and item.Column > self._pivot.TableRange1.Column :
                if not value_row_column.get(item.Row):
                    value_row_column[item.Row] = {item.Column: item.Value}
                else:
                    value_row_column[item.Row].update({item.Column: item.Value})

        year_month_list = []
        uf_list = []
        product_list = []
        unit_list = []
        volume_list = []
        created_at_list = []
        for key_row, value_row in value_row_column.items():
            for key_column, value_column in value_row.items():

                year_month_list.append(f'{year_column.get(key_column)}_\
                    {month_row.get(key_row)}')
                uf_list.append(uf)
                product_list.append(product)
                unit_list.append(unit)
                volume_list.append(value_column)
                created_at_list.append(self.created_time)

        df = pd.DataFrame(list(zip(
                year_month_list,
                uf_list,
                product_list,
                unit_list,
                volume_list,
                created_at_list)
            ), 
            columns=['year_month', 
                'uf',
                'product',
                'unit',
                'volume',
                'created_at'
            ])

        return df

    def execute(self) -> None:
        
        for uf in self._pivot.PivotFields(self.uf_filter).PivotItems():
            self.filter_pivot(pivot=self._pivot, filter=self.uf_filter, value=uf)

            uf_df = []
            path = PathBuilder(folder='output_files', file=f'{uf.Value}.csv').build()
            for product in self._pivot.PivotFields(self.product_filter).PivotItems():
                self.filter_pivot(pivot=self._pivot, filter=self.product_filter, value=product)

                print(f'Building metrics dataframe for product {product} in {uf}..')
                df = self.build_dataframe(uf=uf, product=product, unit='m3')
                uf_df.append(df)

            result_df = pd.concat(uf_df)
            result_df.to_csv(path_or_buf=path, sep=';', index=False, encoding='utf-8-sig')


def main() -> None:
    uf_filter='UN. DA FEDERAÇÃO'
    product_filter='PRODUTO'
    file='vendas-combustiveis-m3.xls'
    sheet='Plan1'

    # Extract sales of oil derivative fuels by UF and product
    ExtractDataFromPivot(
        uf_filter=uf_filter,
        product_filter=product_filter,
        file=file,
        sheet=sheet,
        excel_range='B52'
    ).execute()

    # Extract sales of diesel by UF and type
    ExtractDataFromPivot(
        uf_filter=uf_filter,
        product_filter=product_filter,
        file=file,
        sheet=sheet,
        excel_range='B132'
    ).execute()


if __name__ == '__main__':
    main()