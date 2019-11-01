from text_file_parser import *
from bin_file_parser import *
from data_base_methods import *
from data_find_methods import *

if __name__ == "__main__":
    planner_filename = r'../data/session_00/Planner'
    planner_rsf_filename = r'../data/session_00/Planner.rsf'

    # Парсим текстовый файл
    data_structure, frame_size = parse_text_file(planner_filename)
    # Вычисляем количество кадров
    frame_c = frame_counter(planner_rsf_filename, frame_size)
    # Соединяемся с БД
    cur, conn = connection()
    # Парсим бинарник по кадрам
    with open(planner_rsf_filename, 'rb') as bin_file:
        bin_file.seek(14)
        """
        Начиная с Python 3.8 вы также можете использовать выражения присваивания:
        while buffer := bin_file.read(frame_size * 2):
            process(buffer)
        """
        while True:
            try:
                buffer = bin_file.read(frame_size * 2)
            except EOFError:
                print('EOF')
                break
            data = read_bin_file(data_structure, buffer)
            # ---------------------ЗАПОЛНЯЕМ "BeamTasks"----------------------#
            # Находим группы по "ключевому слову"
            bt, id = find_group(data, 'beamTask')
            item = ['Task', 'taskId']  # [Groupname, parameter] what need to find
            bt_item = find_item(data, item)
            # Добавляем значения из других групп
            add_to(bt, bt_item)
            # Подготавливаем данные для вставки в таблицу
            prepare_data('BeamTasks', bt, cur)
            print(105 * '*')
            # ---------------------ЗАПОЛНЯЕМ "PrimaryMarks"----------------------#
            entity_c = entity_counter(data, 'primaryMark')
            id = 0
            for entity in range(entity_c):
                if entity == 3:
                    breakpoint()
                pm, id = find_group(data, 'primaryMark', id)
                item = ['scanData', 'processingTime',
                        'scanData', 'taskId',
                        'scanData', 'antennaId']
                pm_item = find_item(data, item, id)

                bt_task_id = False
                bt_antenna_id = [1, 2, 3, 4]
                pm_task_id = False
                pm_antenna_id = False

                for group in bt:
                    for i in group:
                        if type(i) is dict:
                            if 'taskId' in i:
                                bt_task_id = i.get('taskId')
                                break

                for i in pm_item:
                    if 'taskId' in i: pm_task_id = i.get('taskId')
                    if 'antennaId' in i: pm_antenna_id = i.get('antennaId')
                    if pm_task_id and pm_antenna_id: break

                if pm_task_id == bt_task_id and pm_antenna_id == bt_antenna_id:
                    # Some convertings with pm
                    add_to(pm, pm_item)

                    # prepare_data(pm, cur, 'PrimaryMarks')
                    print(105 * '*')
