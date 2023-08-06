from dataclasses import dataclass, field, asdict
import logging
import canvasapi
from rich.prompt import Prompt
from rich.progress import track

from .model import get_api_data, reset_api_data, start_month, AC_YEAR


@dataclass
class Answer:  # pylint: disable=too-few-public-methods
    """canvas answer see for complete list of (valid) fields
    https://canvas.instructure.com/doc/api/quiz_questions.html#:~:text=An%20Answer-,object,-looks%20like%3A
    """
    answer_html: str
    answer_weight: int


AnswerOptions = dict[str, int]  # answer_text, answer_weigth


# complete list of params : https://canvas.instructure.com/doc/api/quiz_questions.html


@dataclass
class QuestionDTO:
    answers: list[AnswerOptions]
    question_name: str = ""
    question_type: str = 'multiple_choice_question'  # other option is essay question
    question_text: str = ''
    points_possible: str = '1.0'
    correct_comments: str = ''
    incorrect_comments: str = ''
    neutral_comments: str = ''
    correct_comments_html: str = ''
    incorrect_comments_html: str = ''
    neutral_comments_html: str = ''


@dataclass
class Stats:
    quiz_ids: list[int] = field(default_factory=list)
    question_ids: list[int] = field(default_factory=list)


class CanvasRobot(object):
    account = None

    def __init__(self, account_id=0):
        def login():
            url, key = get_api_data()
            # key = key + 'g'  # force wrong key
            self.canvas = canvasapi.Canvas(url, key)
            self.account = self.canvas.get_account(account_id) if account_id else None
            self.current_user = self.canvas.get_current_user()

        try:
            login()
        except canvasapi.exceptions.InvalidAccessToken:
            logging.debug(f"Invalid Access token, resetting it")
            reset_api_data()
            try:
                login()  # retry once
            except canvasapi.exceptions.InvalidAccessToken:
                logging.debug(f"Invalid Access token on second try")
                raise
        except Exception as e:
            logging.error(f"{e}")
            quit(1)

    # ----------------------------------------

    def get_course(self, course_id: int):
        """"
        :param course_id:
        :returns canvas course with this course_id
        """
        return self.canvas.get_course(course_id)

    def get_courses(self, enrollment_type: str = "teacher"):
        """"
        :enrollment_type 'teacher'(default), 'student','ta', 'observer' 'designer'
        :returns canvas courses for current user in role"""
        return self.canvas.get_courses(enrollment_type=enrollment_type)

    def get_courses_in_account(self, by_teachers: list, this_year=True):
        """get all course in account here use_is has the role/type [enrollment_type]
        :param by_teachers: list of teacher id's
        :param this_year: True=filter courses to include only the current year
        :returns list of courses
        """
        assert self.account, "No (sub) admin account provided"
        courses = []
        for course in self.account.get_courses(by_teachers=by_teachers):
            # only show/insert/update course if current year

            if this_year and (str(course.sis_course_id)[:4] != str(AC_YEAR)
                              or course.name.endswith('conclude')):
                continue
            courses.append(course)
        return courses

    def get_user(self, user_id: int):
        """get user using
        :param user_id:
        :returns user
        """
        return self.canvas.get_user(user_id)

    def create_quiz(self, course_id: int, title: str, quiz_type: str = '') -> (str, int):
        """
        :param course_id:
        :param title:
        :param quiz_type:
        :returns: tuple of msg, quiz_id
        """
        course: Course = self.get_course(course_id)
        quiz = course.create_quiz(dict(title=title, quiz_type=quiz_type))
        logging.debug(f"{course.name} now contains {quiz}")
        return quiz.id

    def create_question(self,
                        course_id: int,
                        quiz_id: int,
                        question_dto: QuestionDTO) -> (str, int):
        """
        :param course_id:
        :param quiz_id:
        :param question_dto:
        :return: quiz_question_id
        """
        course = self.get_course(course_id)
        quiz = course.get_quiz(quiz_id)
        quiz_question = quiz.create_question(question=asdict(question_dto))
        logging.debug(f"{quiz} now contains {quiz_question}")
        return quiz_question.id

    def create_quizzes_from_data(self,
                                 course_id: int,
                                 question_format="Vraag {}.",
                                 data=None
                                 ):
        """
        :param course_id: Canvas course_id: the quizzes are added to this course
        :param question_format: used to create the question name.
        They will be numbered. Should contain '{}' is placehiolder
        starting with 1
        :param data: the quizdata
        :return: stats:Stats
        """
        if '{}' not in question_format:
            msg = (f"parameter 'question_format(={question_format})' "
                   f"should contain {{}} als placeholder")
            ValueError(msg)

        stats = Stats()
        for quiz_name, questions in track(data):

            quiz_id = self.create_quiz(course_id=course_id,
                                       title=quiz_name,
                                       quiz_type="practice_quiz")
            stats.quiz_ids.append(quiz_id)
            for index, (question_text, answers) in enumerate(questions):
                answers_asdict = [asdict(answer) for answer in answers]
                question_dto = QuestionDTO(question_name=question_format.format(index + 1),
                                           question_text=question_text,
                                           answers=answers_asdict)
                question_id = self.create_question(course_id=course_id,
                                                   quiz_id=quiz_id,
                                                   question_dto=question_dto)
                stats.question_ids.append(question_id)

        return stats
