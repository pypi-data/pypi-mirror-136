import os.path
import re
import argparse
import datetime


def create_sql_insert_tuple(meta_line: str, review_line: str):
  meta_columns = meta_line.split(" ")
  date = datetime.datetime.strptime(meta_columns[0], "%m/%d/%Y").strftime("%Y-%m-%d")
  review_id = meta_columns[1]
  reviewer_id = meta_columns[2]
  product_id = meta_columns[3]
  # Y == spam, N == ham
  label = True if meta_columns[4] == 'Y' else False
  star_rating = meta_columns[8][:-1]
  # escape quotes in sql
  review = review_line[:-1].replace("'", "''").replace('"', '""')
  return f"('{date}', '{review_id}', '{reviewer_id}', '{product_id}', {label}, {star_rating}, 'H', '{review}')"


def run():
  # Validation
  parser = argparse.ArgumentParser(description='dataset parser')
  parser.add_argument('meta', type=str, help='path of meta file')
  parser.add_argument('review', type=str, help='path of review file')
  parser.add_argument('target', type=str, help='target path of sql file')
  parser.add_argument('type', type=str, choices=['CH', 'NH', 'ZH'], help='dataset type')
  args = parser.parse_args()
  meta_path = args.meta
  review_path = args.review
  target_path = args.target
  dataset_type = args.type

  if not (os.path.isfile(meta_path) or not os.path.isfile(review_path)):
    parser.print_help()
    exit(1)

  chicago_pattern = r'^([1-9]|1[0-2])/([1-9]|1[0-9]|2[0-9]|3[01])/\d{4} [^ ]+ [^ ]+ [^ ]+ [Y|N] \d+ \d+ \d+ \d+$'
  chicago_matcher = re.compile(chicago_pattern)
  with open(meta_path, 'r') as meta_file, open(review_path, 'r') as review_file:
    meta_line_count = 0
    for m in meta_file:
      meta_line_count += 1
      if not chicago_matcher.match(m):
        print('meta line does not match' + chicago_pattern)
        exit(1)

    review_line_count = 0
    for r in review_file:
      review_line_count += 1

    if review_line_count != meta_line_count:
      print('Line numbers of review file and meta file differ')
      exit(1)

    # reset read position
    meta_file.seek(0, 0)
    review_file.seek(0, 0)
    # create sql file
    with open(target_path, 'w') as target_file:
      insert_chicago_insert_preamble = "INSERT INTO public.review(date, review_id, reviewer_id, product_id, spam, " \
                                       "rating, facility, review)\nVALUES\n"
      target_file.write(insert_chicago_insert_preamble)
      for i in range(review_line_count):
        current_meta_line = meta_file.readline()
        current_review_line = review_file.readline()
        # last line
        if i == review_line_count - 1:
          # last insert row tuple ends with ;
          target_file.write(create_sql_insert_tuple(current_meta_line, current_review_line) + ';\n')
        else:
          target_file.write(create_sql_insert_tuple(current_meta_line, current_review_line) + ',\n')


if __name__ == "___main__":
  run()
