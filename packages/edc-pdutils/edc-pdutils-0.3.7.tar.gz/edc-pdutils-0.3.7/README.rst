|pypi| |actions| |codecov| |downloads|

edc-pdutils
+++++++++++

Use pandas with the Edc


To export Crf data, for example:

.. code-block:: python

    csv_path = '/Users/erikvw/Documents/ambition/export/'
    date_format = '%Y-%m-%d'
    sep = ','

    class MyDfHandler(CrfDfHandler):
        visit_tbl = 'ambition_subject_subjectvisit'
        exclude_columns = ['form_as_json', 'survival_status','last_alive_date',
                           'screening_age_in_years', 'registration_datetime',
                           'subject_type']

    class MyCsvCrfTablesExporter(CsvCrfTablesExporter):
        visit_columns = ['subject_visit_id']
        datetime_fields = ['randomization_datetime']
        df_handler_cls = MyDfHandler
        app_label = 'ambition_subject'
        export_folder = csv_path

    sys.stdout.write('\n')
    exporter = MyCsvCrfTablesExporter()
    exporter.to_csv(date_format=date_format, delimiter=sep)

To export INLINE data for any CRF configured with an inline, for example:

.. code-block:: python

    class MyDfHandler(CrfDfHandler):
        visit_tbl = 'ambition_subject_subjectvisit'
        exclude_columns = ['form_as_json', 'survival_status','last_alive_date',
                           'screening_age_in_years', 'registration_datetime',
                           'subject_type']


    class MyCsvCrfInlineTablesExporter(CsvCrfInlineTablesExporter):
        visit_columns = ['subject_visit_id']
        df_handler_cls = MyDfHandler
        app_label = 'ambition_subject'
        export_folder = csv_path
        exclude_inline_tables = [
            'ambition_subject_radiology_abnormal_results_reason',
            'ambition_subject_radiology_cxr_type']
    sys.stdout.write('\n')
    exporter = MyCsvCrfInlineTablesExporter()
    exporter.to_csv(date_format=date_format, delimiter=sep)


Settings
========

``EXPORT_FILENAME_TIMESTAMP_FORMAT``: True/False (Default: False)

By default a timestamp of the current date is added as a suffix to CSV export filenames.

By default a timestamp of format ``%Y%m%d%H%M%S`` is added.

``EXPORT_FILENAME_TIMESTAMP_FORMAT`` may be set to an empty string or a valid format for ``strftime``.

If ``EXPORT_FILENAME_TIMESTAMP_FORMAT`` is set to an empty string, "", a suffix is not added.

For example:

.. code-block:: bash

    # default
    registered_subject_20190203112555.csv

    # EXPORT_FILENAME_TIMESTAMP_FORMAT = "%Y%m%d"
    registered_subject_20190203.csv

    # EXPORT_FILENAME_TIMESTAMP_FORMAT = ""
    registered_subject.csv

.. |pypi| image:: https://img.shields.io/pypi/v/edc-pdutils.svg
    :target: https://pypi.python.org/pypi/edc-pdutils

.. |actions| image:: https://github.com/clinicedc/edc-pdutils/workflows/build/badge.svg?branch=develop
  :target: https://github.com/clinicedc/edc-pdutils/actions?query=workflow:build

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-pdutils/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-pdutils

.. |downloads| image:: https://pepy.tech/badge/edc-pdutils
   :target: https://pepy.tech/project/edc-pdutils
