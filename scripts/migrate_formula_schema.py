import pandas as pd
from sqlalchemy import create_engine, text
import json
import os

def main():
    db_uri = 'postgresql://sg_user:sg_password@localhost:5432/sg_proj_004'
    engine = create_engine(db_uri)

    # 정의된 기준
    properties_keys = {'N.V', 'VIS', '점착력', 'Tg', '내충격BA', '내충격#4'}
    additives_keys = {'EAc', 'Eac(LAB)', 'Toluene', '기타 첨가제', 'Hardener', 'Tackifier'}

    count = 0
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, formula_data FROM adhesive_recipes"))
        rows = result.fetchall()
        
        for row in rows:
            row_id = row[0]
            f_data = row[1]
            
            try:
                f = json.loads(f_data) if isinstance(f_data, str) else f_data
                if isinstance(f, str): f = eval(f)
                
                # 이미 변환된 데이터 스킵
                if 'monomers' in f and 'properties' in f:
                    continue
                    
                new_f = {
                    'monomers': {},
                    'additives': {},
                    'properties': {}
                }
                
                for k, v in f.items():
                    if k in properties_keys:
                        new_f['properties'][k] = float(v)
                    elif k in additives_keys:
                        new_f['additives'][k] = float(v)
                    else:
                        new_f['monomers'][k] = float(v)
                        
                conn.execute(text("UPDATE adhesive_recipes SET formula_data = :f WHERE id = :id"), 
                             {"f": json.dumps(new_f), "id": row_id})
                count += 1
            except Exception as e:
                print(f"Error migrating row {row_id}: {e}")
        conn.commit()
    print(f"Migration completed. Migrated {count} rows.")

if __name__ == '__main__':
    main()
