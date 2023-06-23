import unittest
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi_sql_profiler.middleware import SQLProfilerMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from fastapi_sql_profiler.database import Base, engine


class TestSQLTap(unittest.TestCase):

    def setUp(self):
        self.app = FastAPI()
        self.client = TestClient(self.app)
        self.engine = engine
        # Base = declarative_base()
        class Item(Base):
            __tablename__ = "item"
            id = Column("id", Integer, primary_key=True)
            name = Column("name", String)
            description = Column("description", String)
        self.Item = Item

        class ItemSchema(BaseModel):
            name: str
            description: str = None

            class Config:
                orm_mode = True
        self.ItemSchema = ItemSchema

        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.app.add_middleware(SQLProfilerMiddleware, engine=self.engine)

    def insert_api(self):
        @self.app.post('/item_create')
        async def create(itemschema: self.ItemSchema):
            session = self.Session()
            item_data = self.Item(name=itemschema.name, description=itemschema.description)
            session.add(item_data)
            session.commit()
            return item_data
        payload = {
            'name':'item1',
            'description':'first item'
        }
        response = self.client.post('/item_create', json=payload)
        return response

    def display_api(self):
        @self.app.get("/item_get")
        def show():
            session = self.Session()
            return session.query(self.Item).all()
        response = self.client.get('/item_get')
        return response

    def update_api(self):
        @self.app.put('/item_update/{id}')
        def update(id: int, itemschema: self.ItemSchema):
            session = self.Session()
            item = session.query(self.Item).filter_by(id=id).first()
            if not item:
                return {"message":f"Item with the id {id} is not available"}
            item.name = itemschema.name
            item.description = itemschema.description
            session.add(item)
            session.commit()
            return item
        payload = {
            'name':'itemupdate',
            'description':'updateditem'
        }
        response = self.client.put('/item_update/1', json=payload)
        return response

    def delete_api(self):
        @self.app.delete("/item_delete/{id}")
        def delete(id: int):
            session = self.Session()
            item = session.query(self.Item).filter_by(id=id)
            if not item.first():
                return {"message":f"Item with the id {id} is not available"}
            item.delete()
            session.commit()
            return {"message": "Item delete Successfully"}
        response = self.client.delete('/item_delete/1')
        return response

    def test_request(self):
        """ Call API"""
        insert_response = self.insert_api()
        display_response = self.display_api()
        update_response = self.update_api()
        delete_response = self.delete_api()

        self.assertEqual(insert_response.status_code, 200)
        self.assertEqual(display_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)


    def tearDown(self):
        """Clean up the database"""
        session = self.Session()
        session.execute(text('DELETE FROM item'))
        session.execute(text('DELETE FROM middleware_query'))
        session.execute(text('DELETE FROM middleware_requests'))
        session.commit()
        session.close()

