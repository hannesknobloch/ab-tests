USE testdb;

CREATE TABLE ab_test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    variant_id INT NOT NULL,
    test_id VARCHAR(100) NOT NULL,
    views INT,
    clicks INT,
    ctr DECIMAL(5,2)
);