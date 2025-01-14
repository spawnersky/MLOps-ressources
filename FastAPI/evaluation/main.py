from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from enum import Enum
from typing import Optional, Set
from fastapi.responses import JSONResponse


from helpers import file, database, test_name, subject_name, questions_selection

api = FastAPI(title='QCM API')




class TestName(str, Enum):
    # for i in range(len_test):
    #     test = test_name[i]
    test_1 = test_name[0]
    test_2 = test_name[1]
    test_3 = test_name[2]

class SubjectName(str, Enum,):
    subject_1 = subject_name[0]
    subject_2 = subject_name[1]
    subject_3 = subject_name[2]
    subject_4 = subject_name[3]
    subject_5 = subject_name[4]
    subject_6 = subject_name[5]
    subject_7 = subject_name[6]
    subject_8 = subject_name[7]

class Question(int, Enum):
    len_1 = 5
    len_2 = 10
    len_3 = 20

    
class MyException(Exception):
    def __init__(self, allowed_subject:list):
        self.allowed_subject = allowed_subject

@api.exception_handler(MyException)
def MyExceptionHandler(
    request: Request,
    exception: MyException
    ):
    return JSONResponse(
        status_code=418,
        content={
            'url': str(request.url),
            'message': f"Oops! The subject does not exist for this test. Please select a subject among the following \
            list: {exception.allowed_subject}",
            # 'allowed_subject':exception.allowed_subject 
        }
    )



## Identity & Access Management

security = HTTPBasic()



def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):

    if (not credentials.username=='bob' or not credentials.password=='builder') and \
       (not credentials.username=='alice' or not credentials.password=='wonderland') and \
       (not credentials.username=='clementine' or not credentials.password=='mandarine'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# method that generates questions

@api.get("/get_questions/{test_name}/{nb_questions:int}/{subject_name_1}")
async def get_questions(
                    test_name: TestName, 
                    nb_questions:Question, 
                    subject_name_1: SubjectName,
                    subject_name_2: Optional[SubjectName] = None,
                    subject_name_3: Optional[SubjectName] = None,
                    subject_name_4: Optional[SubjectName] = None,
                    subject_name_5: Optional[SubjectName] = None,
                    subject_name_6: Optional[SubjectName] = None,
                    subject_name_7: Optional[SubjectName] = None,
                    subject_name_8: Optional[SubjectName] = None,
                    username: str = Depends(get_current_username)):
    """
     This method returns questions according to type of test (unique value expected), subjects (multiple selection allowed) 
    and finally number of questions wanted (among 5, 10 or 20)
    
    """
    try:
        subjects_allowed = set(file[file.use==test_name].subject.to_list())

        tmp = [subject_name_1 , subject_name_2 , subject_name_3 , subject_name_4,
                subject_name_5,subject_name_6, subject_name_7, subject_name_8]

        subject = [x for x in tmp if x is not None]
    

        result = questions_selection(test=test_name, subjects=subject, nb_questions=nb_questions)

    except IndexError:
        raise MyException(
            allowed_subject = subjects_allowed
            )        

    
    return {'result': result,
            "username": username}
    


## ADMIN PART
def admin_access(credentials: HTTPBasicCredentials = Depends(security)):
    
    if not credentials.username=='admin' or not credentials.password=='4dm1N':  
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"}
        )

    return credentials.username


new_questions = []

@api.post("/create_questions")
async def create_questions(question: str, username: str = Depends(admin_access)):
    """
     This method enables an admin user to create a new question that will be stored in list of new questions
    """
    try:
        new_questions.append(question)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail='Bad Type'
        )       

    return {'new question created': question,
            "list of new questions created so far": new_questions}




