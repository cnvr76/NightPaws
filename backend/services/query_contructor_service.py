from typing import List, Set, Dict, Tuple, Optional
from models import Application
from config.logger import Logger
from models import ChainComponent
from datetime import datetime


logger = Logger(__name__).configure()


class QueryConstructor:
    def __init__(self) -> None:
        # convert to dict later for better performance
        self.filters: str = f"-from:linkedin -from:support@ -from:jooble -from:djinni -category:promotions -list:matches"
        self.skip_company_words = (
            "a.s.", "alerts", "alert", "job", "s.r.o.", "hr",
        )
        self.skip_email_words = (
             "noreply@", "jobs@", "careers@", "alerts", "alert",      
        )
        self.skip_body_words = (
            "automated",
        )
        self.status_words = (
            "unfortunately",
        )

    
    def construct_queries(self, application: Application) -> Tuple[Optional[str], ...]:
        q1 = self._construct_wide_query(application)
        q2 = self._construct_company_query(application)
        q3 = self._construct_company_query(application, full_name=True)
        return (q1, q2, q3)


    def _construct_wide_query(self, application: Application) -> Optional[str]:
        # from:(hyperia.sk) AND ((hyperia) OR/AND (python OR developer OR študent)) AND in:inbox
        parts: List[str] = []
        
        known_senders: Set[str] = self.__get_known_senders(application) # maybe this won't be needed at all
        if known_senders:
            sender_query = " OR ".join([f"from:{sender}" for sender in known_senders])
            parts.append(f"({sender_query})")

        clean_company: str = self.__get_clean_string(application.company_name, self.skip_company_words)
        clean_company_words: List[str] = clean_company.split()
        company_query: str = clean_company_words[0]

        clean_title: List[str] = application.job_title.lower().split()
        title_query: str = " OR ".join([f'{word}' for word in clean_title if len(word) > 2])

        if title_query and company_query:
            # keyword_query = f'(({title_query}) {"OR" if known_senders else "AND"} {company_query})'
            keyword_query = f'(({title_query}) AND {company_query})'
            parts.append(keyword_query)

        if not parts:
            logger.warn(f"No parts were found: {parts}")
            return None

        final_query: str = (
            f'{" OR ".join(parts)} '
            # f'AND after:{self.__get_date(application)} '
            f'AND in:inbox {self.filters}'
        )
        return final_query


    def _construct_company_query(self, application: Application, full_name: bool = False) -> Optional[str]:
        # from:hyperia {filters} in:inbox - full company name, not just the first word
        clean_company: str = self.__get_clean_string(application.company_name, self.skip_company_words)
        company_query: str = clean_company
        if not full_name:
            clean_company_words: List[str] = clean_company.split()
            company_query = clean_company_words[0]
        
        final_query: str = (
            f'from:{company_query} '
            # f'AND after:{self.__get_date(application)}'
            f'AND in:inbox {self.filters}'
        )
        return final_query


    def __get_clean_string(self, string: str, skip_words: Tuple[str, ...]) -> str:
        for word in skip_words:
            clean_string: str = string.replace(word, "")
        return clean_string.strip().lower()
    

    def __get_date(self, application: Application) -> str:
        last_date: datetime = application.email_chain[-1]["received_at"] if len(application.email_chain) > 0 else application.created_at
        return last_date.strftime('%Y/%m/%d')
    

    def __get_known_senders(self, application: Application) -> Set[str]:
        chains: List[ChainComponent] = application.email_chain
        known_senders: Set[str] = set()
        for component in chains:
            known_senders.add(component["sender"]["email"])
        return known_senders