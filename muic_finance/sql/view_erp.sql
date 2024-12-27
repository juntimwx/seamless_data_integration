SELECT erp.[year] ,
	erp.trimester ,
	erp.[day] ,
	erp.[month] ,
	erp.doc_no ,
	erp.doc_date ,
	erp.funds_center ,
	erp.cost_center_id ,
	CASE WHEN cost_centralize = 'NULL' THEN 'CostCenter'
		WHEN cost_centralize IS NULL THEN 'CostCenter'
	ELSE cost_centralize END AS 'CostCentralize',
	erp.io_good_id ,
	erp.io_work_id ,
	erp.io_activity_id ,
	erp.io_project_id ,
	erp.order_description ,
	erp.hrot ,
	generalLadger.id general_ledger_id ,
	generalLadger.description general_ledger_description ,
	erp.amount ,
	erp.detail ,
	erp.mu_strategy_id ,
	erp.ic_strategy_id ,
	costCenter.description cost_center_description ,
	costCenter.name_en cost_center_name_en ,
	costCenter.name_th cost_center_name_th ,
	generalLadger.group_id ,
	generalLadger.group_description,
	icStrategy.name ic_strategy_name,
	icStrategy.description ic_strategy_description,
	muStrategy.name mu_strategy_name,
	muStrategy.description mu_strategy_description,
	ioGood.description io_good_description,
	ioWork.description io_work_description,
	ioActivity.description io_activity_description,
	ioProject.description io_project_description
FROM muic_finance.dbo.erp_2023 erp
LEFT JOIN muic_finance.master.master_cost_center costCenter ON erp.cost_center_id = costCenter.id 
LEFT JOIN muic_finance.master.master_general_ledger generalLadger ON erp.general_ledger_id = generalLadger.id 
LEFT JOIN muic_finance.master.master_ic_strategy icStrategy ON erp.ic_strategy_id = icStrategy.id 
LEFT JOIN muic_finance.master.master_mu_strategy muStrategy ON erp.mu_strategy_id = muStrategy.id 
LEFT JOIN muic_finance.master.master_io_activities ioActivity ON erp.io_activity_id = ioActivity.id 
LEFT JOIN muic_finance.master.master_io_goods ioGood ON erp.io_good_id = ioGood.id 
LEFT JOIN muic_finance.master.master_io_projects ioProject ON erp.io_project_id = ioProject.id 
LEFT JOIN muic_finance.master.master_io_works ioWork ON erp.io_work_id = ioWork.id