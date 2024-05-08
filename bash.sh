mkdir -p $3/pharma_gyan_proj/application_config
cp -R $3/application_configs/$1/$2/* $3/pharma_gyan_proj/application_config/
mkdir -p $3/pharma_gyan_proj/pharma_gyan_proj/templates/bank_templates/documents
cp $3/application_configs/$1/templates/documents/* $3/pharma_gyan_proj/pharma_gyan_proj/templates/bank_templates/documents/