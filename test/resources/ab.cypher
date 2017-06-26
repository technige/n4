CREATE (a:Person {name:'Alice'}) RETURN a;
CREATE (b:Person {name:'Bob'}) RETURN b;

MATCH (a:Person {name:'Alice'})
MATCH (b:Person {name:'Bob'})
MERGE (a)-[:KNOWS]->(b);
