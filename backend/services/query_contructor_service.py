from typing import List, Set, Tuple, Optional
from models import Application, SenderInfo
from config.logger import Logger
from models import ChainComponent
from datetime import datetime, timedelta


logger = Logger(__name__).configure()


class QueryConstructor:
    def __init__(self) -> None:
        self.platform_filters: str = "-from:linkedin -from:support@ -from:jooble -from:djinni"
        self.system_filters: str = "-category:social"
        self.filters: str = f"{self.platform_filters} {self.system_filters}"
        self.skip_company_words: Set[str] = set((
            "a.s", "a. s", "a.s.", "a. s.", "alerts", "alert", "job", 
            "s.r.o", "s. r. o", "s.r.o.", "s. r. o.", "hr", ",", ".", "-", "_"
        ))

    
    def construct_queries(self, application: Application) -> Tuple[Optional[str], ...]:
        q1 = self._construct_wide_query(application)
        q2 = self._construct_company_query(application)
        q3 = self._construct_company_query(application, full_name=True)
        return q1, q2, q3


    def _construct_wide_query(self, application: Application) -> Optional[str]:
        # (from:Dasa.Noskovicova@adastragrp.com OR from:Noskovicova, Dasa OR from:Dasa Noskovicova) OR ((junior OR data OR analyst) AND adastra) AND -from:me + filters
        parts: List[str] = []
        
        known_senders: Set[str] = self.__get_known_senders(application) # maybe this won't be needed at all
        if known_senders:
            sender_query = " OR ".join(f"from:{sender}" for sender in known_senders)
            parts.append(f"({sender_query})")

        clean_company: str = self.__get_clean_string(application.company_name, self.skip_company_words)
        clean_company_words: List[str] = clean_company.split()
        company_query: str = clean_company_words[0]

        clean_title: List[str] = application.job_title.lower().split()
        title_query: str = " OR ".join(f'{word}' for word in clean_title if len(word) > 2)

        if title_query and company_query:
            # keyword_query = f'(({title_query}) {"OR" if known_senders else "AND"} {company_query})'
            keyword_query = f'(({title_query}) AND {company_query})'
            parts.append(keyword_query)

        if not parts:
            logger.warn(f"No parts were found: {parts}")
            return None

        final_query: str = (
            f'{" OR ".join(parts)} '
            f'AND after:{self.__get_date(application)} '
            f'AND -from:me {self.filters}'
        )
        return final_query


    def _construct_company_query(self, application: Application, full_name: bool = False) -> Optional[str]:
        # (subject:"adastra" OR subject:"adastra") OR from:adastra AND -from:me + filters
        clean_company: str = self.__get_clean_string(application.company_name, self.skip_company_words)
        company_query: str = clean_company
        if not full_name:
            clean_company_words: List[str] = clean_company.split()
            company_query = clean_company_words[0]

        subject_query: str = f'subject:"{company_query}" OR subject:"{clean_company}"'
        
        final_query: str = (
            f'({subject_query}) OR '
            f'from:{company_query} '
            f'AND after:{self.__get_date(application)}'
            f'AND -from:me {self.filters}'
        )
        return final_query


    def __get_clean_string(self, string: str, skip_words: Tuple[str, ...]) -> str:
        string = string.lower()
        for word in skip_words:
            string = string.replace(word, "")
        return " ".join(string.split())
    

    def __get_date(self, application: Application) -> str:
        raw_date: str | datetime = application.email_chain[0]["received_at"] if len(application.email_chain) > 0 else application.applied_at
        last_date: datetime = datetime.fromisoformat(raw_date) if isinstance(raw_date, str) else raw_date
        last_date = last_date - timedelta(days=1)
        return last_date.strftime('%Y/%m/%d')
    

    def __get_known_senders(self, application: Application) -> Set[str]:
        chains: List[ChainComponent] = application.email_chain
        known_senders: Set[str] = set()
        for component in chains:
            sender: SenderInfo = component["sender"]
            known_senders.add(sender["email"])
            known_senders.add(sender["name"])
        return known_senders