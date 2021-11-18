workspace {

    model {
        customer = person "Trader" "Trader usando el software para hace un backtest de una estrategia." "Customer"
        enterprise "Memoria" {
         memoria = softwaresystem "Bot" "Software de trading algorítmico" {
                bot = container "BOT" "bot" "Python3" {
                    main_controller = component "Main" "Thread principal del software" "Python3" ""
                    data = component "Data" "Lectura de datos hacia la bd" "Python3" ""
                    visualization = component "Visualizacion" "visualizacion" "Python3" ""    
                }
                
                strategies = container "Estrategias" "estrategias" "Python3" "" {
                    nlp_strats = component "NLP Strategies" "Estrategias en base a noticias" "Python3" ""
                    ta_strats = component "TA Strategies" "Estratregias en base a Analisis Tecnico" "Python3" ""
                    
                }
                processing = container "Procesamiento" "procesamiento" "Python3" "" {
                    backtest = component "Backtest" "Obtenemos KPIs relacionados al backtest" "Python3" ""
                    optimizing = component "Optimizacion" "Optimizacion de estrategias" "Python3" ""
                }
                
                data_extractor = container "DataExtractor" "extraccion de datos" "Python3" ""
                db = container "Database" "Data sobre trades" "MySQL" "Database"
            }
            
            
        }
       
        bot -> processing "Pide mejores trades"
        processing -> db "Lee y escribe"
        processing -> strategies "Pide estrategias"
        data_extractor -> db "Escribe noticias"
        
    }

    views {
        systemlandscape "SystemLandscape" {
            include *
            autoLayout
        }
        
        systemcontext memoria "SystemContext" {
            include *
            autoLayout
        }
        
        container memoria "Containers" {
            include *
            
            autoLayout
        }
        
        dynamic processing "Procesamiento" "Procesamiento y Optimizacion de estrategias para obtener los KPIs de 1 o mas estrategias" {
            bot -> optimizing "Gatilla optimizacion de estrategias"
            optimizing -> strategies "Pide backtest de estrategia"
            strategies -> bot "Pide data historica"
            bot -> db "Lee data"
            db -> bot "Retorna data"
            bot -> strategies "Restorna data"
            strategies -> optimizing "Retorna resultados del backtest"
            optimizing -> bot "Retorna mejores trades"
            bot -> backtest "Pide calcular KPIs de los backtests"
            backtest -> bot "Retorna KPIs"
            autoLayout
        }
    

        styles {
            element "Person" {
                color #ffffff
                fontSize 22
                shape Person
            }
            element "Customer" {
                background #08427b
            }
            element "Bank Staff" {
                background #999999
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Existing System" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Web Browser" {
                shape WebBrowser
            }
            element "Mobile App" {
                shape MobileDeviceLandscape
            }
            element "Database" {
                shape Cylinder
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Failover" {
                opacity 25
            }
        }
    }
    
}