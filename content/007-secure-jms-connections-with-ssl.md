Title: Защищаем JMS соединения с помощью SSL
Slug: secure-jms-connections-with-ssl
Authors: Oleg Lomaka
Date: 2011-11-11 13:33
Category: blog
Tags: ActiveMQ, Java, JMS

Допустим, есть у нас задача раскинуть выполнение некой произвольной очереди заданий на несколько компьютеров. Основные условия этой задачи примерно такие:

 - Менеджер заданий и сам исполнитель (воркер) должны быть упакованы в одно приложение. Это дает возможность не напрягаться с установкой каких-то сложных систем. Запустили приложение — оно что-то вычисляет само для себя. Хотим ускорить процесс — запускаем на соседнем компьютере его-же в качестве клиента к первому, и все делается в два раза быстрее.
 - Задачи раздаются через JMS.
 - К JMS брокеру нельзя присоединиться кому попало. Т.е. нужна идентификация.
 - Не должно быть возможности прослушать трафик между менеджером и воркером.

Саму задачу я решал с помощью ActiveMQ и spring-jms. В классической схеме, мы должны создать сертификат для брокера. Создать сертификат для каждого клиента. Настроить SslContext брокера для использования в качестве KeyStore своего сертификата и в качестве TrustStore сертификатов клиентов. В окружениях клиентов прописать использование правильных сертификатов. В нашем случае есть несколько оговорок или упрощений:

 - Брокер должен требовать от клиента сертификат для идентификации.
 - Мы не должны менять глобальные настройки SSL клиента, как это рекомендуется в классической схеме. Его основной KeyStore может использоваться другими частями приложения. И KeyStore, используемый для соединения с брокером не должен конфликтовать с основным.
 - Нам хватит одного сертификата для обоих сторон, т.к. и клиент и сервер — части одного и того-же приложения.

Первым делом генерируем новый KeyStore, который будет упакован в jar приложения.

    :::bash
    keytool -genkey -alias broker -keyalg RSA -keystore broker.ks

Далее в конфигурации Spring контейнера настраиваем запуск брокера с обязательной идентификацией клиента по сертификату

    :::xml
	<amq:broker brokerName="ActiveMQBroker" useJmx="false"
				persistent="false" >
		<amq:sslContext>
			<amq:sslContext keyStore="classpath:broker.ks"
							keyStorePassword="123456" 
							trustStore="classpath:broker.ks"
							trustStorePassword="123456" />
			</amq:sslContext>
			<amq:transportConnectors>
				<amq:transportConnector uri="ssl://localhost:61616?needClientAuth=true"></amq:transportConnector>
			</amq:transportConnectors>
	</amq:broker>

И с этим же сертификатом настраиваем соединения к этому брокеру.

    :::xml
	<bean id="jmsFactory" 
		  class="org.apache.activemq.pool.PooledConnectionFactory"
		  destroy-method="stop">
		<property name="connectionFactory">
			<bean class="org.apache.activemq.ActiveMQSslConnectionFactory">
				<property name="brokerURL">
					<value>ssl://localhost:61616</value>
				</property>
				<property name="keyStore" value="broker.ks" />
				<property name="keyStorePassword" value="123456" />
				<property name="trustStore" value="broker.ks" />
				<property name="trustStorePassword" value="123456" />
			</bean>
		</property>
	</bean>
	
В обоих случаях blocker.ks лежит прямо в jar файле, а пути к нему прописываются немного по разному. В зависимости от того, как каждый класс осуществляет доступ к ресурсам.

Пример использования этих кусков конфигурации можно посмотреть в демонстрационном приложении [Sample Spring-Jms](https://github.com/olomix/spring-jms).
